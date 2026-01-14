from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, Value, Count
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone

from apps.invoices.models import Invoice
from apps.credit_notes.models import CreditNote
from apps.suppliers.models import Supplier
from apps.accounts.permissions import IsFinanceUser


@extend_schema(
    summary="Tableau de bord",
    description="Statistiques générales pour le dashboard"
)
@api_view(['GET'])
@permission_classes([IsFinanceUser])
def dashboard(request):
    """
    Endpoint pour le dashboard avec statistiques générales
    """
    try:
        # Date actuelle
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # Query params for filtering
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        supplier_id = request.query_params.get('supplier')
        
        # Validate month/year if provided
        if month and year:
            try:
                month = int(month)
                year = int(year)
            except ValueError:
                return Response({'error': 'Invalid month or year format'}, status=400)
        else:
            month = current_month
            year = current_year
        
        # Statistiques générales (toujours sur toute la base, non filtrées)
        total_suppliers = Supplier.objects.filter(is_active=True).count()
        
        # Base querysets pour les KPIs filtrés
        filtered_invoices = Invoice.objects.filter(is_active=True)
        filtered_credit_notes = CreditNote.objects.filter(is_active=True)
        
        # Apply supplier filter if provided (sauf pour total_suppliers)
        if supplier_id:
            filtered_invoices = filtered_invoices.filter(supplier_id=supplier_id)
            filtered_credit_notes = filtered_credit_notes.filter(supplier_id=supplier_id)
        
        # Statistiques de toute la base (avec filtres)
        total_invoices_all = filtered_invoices.aggregate(
            total=Sum('net_to_pay')
        )['total'] or Decimal('0.00')
        
        total_credit_notes_all = filtered_credit_notes.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_all = total_invoices_all - total_credit_notes_all
        
        # Statistiques de l'année actuelle (avec filtres)
        year_invoices = filtered_invoices.filter(year=year)
        year_credit_notes = filtered_credit_notes.filter(year=year)
        
        total_invoices_year = year_invoices.aggregate(
            total=Sum('net_to_pay')
        )['total'] or Decimal('0.00')
        
        total_credit_notes_year = year_credit_notes.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_year = total_invoices_year - total_credit_notes_year
        
        # Statistiques du mois demandé (avec filtres)
        current_month_invoices = filtered_invoices.filter(
            month=month,
            year=year
        )
        
        current_month_credit_notes = filtered_credit_notes.filter(
            month=month,
            year=year
        )
        
        total_invoices_current = current_month_invoices.aggregate(
            total=Sum('net_to_pay')
        )['total'] or Decimal('0.00')
        
        total_credit_notes_current = current_month_credit_notes.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_current_month = total_invoices_current - total_credit_notes_current
        
        # Top 5 fournisseurs (avec filtres)
        top_suppliers = filtered_invoices.values(
            'supplier__name',
            'supplier__code'
        ).annotate(
            total_amount=Sum('net_to_pay')
        ).order_by('-total_amount')[:5]
        
        # Dernières factures (avec filtres)
        recent_invoices = Invoice.objects.filter(
            is_active=True
        )
        if supplier_id:
            recent_invoices = recent_invoices.filter(supplier_id=supplier_id)
        
        recent_invoices = recent_invoices.select_related('supplier').order_by('-created_at')[:10]
        
        recent_invoices_data = []
        for invoice in recent_invoices:
            recent_invoices_data.append({
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'supplier_name': invoice.supplier.name,
                'net_to_pay': float(invoice.net_to_pay),
                'month': invoice.month,
                'year': invoice.year,
                'created_at': invoice.created_at.isoformat()
            })
        
        # Statistiques du mois actuel (pour compatibilité frontend)
        current_month_invoices = Invoice.objects.filter(
            month=current_month,
            year=current_year,
            is_active=True
        )
        
        current_month_credit_notes = CreditNote.objects.filter(
            month=current_month,
            year=current_year,
            is_active=True
        )
        
        total_invoices_current = current_month_invoices.aggregate(
            total=Sum('net_to_pay')
        )['total'] or Decimal('0.00')
        
        total_credit_notes_current = current_month_credit_notes.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_current_month = total_invoices_current - total_credit_notes_current
        
        return Response({
            'period': {
                'current_month': current_month,
                'current_year': current_year,
                'month_name': _(f"Month {current_month}")
            },
            'filter_info': {
                'month': month,
                'year': year,
                'supplier_id': supplier_id
            },
            'overview': {
                'total_suppliers': total_suppliers,
                'current_month': {
                    'total_invoices': float(total_invoices_current),
                    'total_credit_notes': float(total_credit_notes_current),
                    'net_amount': float(net_current_month),
                    'invoice_count': current_month_invoices.count(),
                    'credit_note_count': current_month_credit_notes.count()
                },
                'all_time': {
                    'total_invoices': float(total_invoices_all),
                    'total_credit_notes': float(total_credit_notes_all),
                    'net_amount': float(net_all),
                    'invoice_count': filtered_invoices.count(),
                    'credit_note_count': filtered_credit_notes.count()
                },
                'year_to_date': {
                    'total_invoices': float(total_invoices_year),
                    'total_credit_notes': float(total_credit_notes_year),
                    'net_amount': float(net_year),
                    'invoice_count': year_invoices.count(),
                    'credit_note_count': year_credit_notes.count()
                }
            },
            'top_suppliers': [
                {
                    'supplier_name': item['supplier__name'],
                    'supplier_code': item['supplier__code'],
                    'total_amount': float(item['total_amount'])
                }
                for item in top_suppliers
            ],
            'recent_invoices': recent_invoices_data,
            'status': 'healthy'
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la génération du dashboard: {str(e)}',
            'status': 'error'
        }, status=500)


@extend_schema(
    summary="Rapport financier mensuel",
    description=(
        "Rapport agrégé sur un mois/année: totaux factures/avoirs et ventilation par fournisseur. "
        "Paramètres requis: month, year"
    )
)
@api_view(['GET'])
@permission_classes([IsFinanceUser])
def monthly_report(request):
    month = request.query_params.get('month')
    year = request.query_params.get('year')

    if not month or not year:
        return Response({'error': _('Les paramètres month et year sont obligatoires')}, status=400)

    try:
        month_int = int(month)
        year_int = int(year)
        if not (1 <= month_int <= 12):
            raise ValueError
    except ValueError:
        return Response({'error': _('Paramètres month et year invalides')}, status=400)

    invoices_qs = Invoice.objects.filter(month=month_int, year=year_int, is_active=True)
    credit_notes_qs = CreditNote.objects.filter(month=month_int, year=year_int, is_active=True)

    invoices_by_supplier = invoices_qs.values(
        'supplier_id',
        'supplier__name',
        'supplier__code',
    ).annotate(
        invoice_count=Count('id'),
        total_amount=Sum('net_to_pay'),
    )

    credit_notes_by_supplier = credit_notes_qs.values(
        'supplier_id',
        'supplier__name',
        'supplier__code',
    ).annotate(
        credit_note_count=Count('id'),
        total_credit_amount=Sum('amount'),
    )

    invoices_map = {}
    for row in invoices_by_supplier:
        invoices_map[row['supplier_id']] = {
            'supplier': {
                'id': str(row['supplier_id']),
                'name': row.get('supplier__name'),
                'code': row.get('supplier__code'),
            },
            'invoiceCount': int(row.get('invoice_count') or 0),
            'totalAmount': float(row.get('total_amount') or Decimal('0.00')),
            'creditNoteCount': 0,
            'totalCreditAmount': 0.0,
        }

    credit_notes_map = {}
    for row in credit_notes_by_supplier:
        credit_notes_map[row['supplier_id']] = {
            'supplier': {
                'id': str(row['supplier_id']),
                'name': row.get('supplier__name'),
                'code': row.get('supplier__code'),
            },
            'invoiceCount': 0,
            'totalAmount': 0.0,
            'creditNoteCount': int(row.get('credit_note_count') or 0),
            'totalCreditAmount': float(row.get('total_credit_amount') or Decimal('0.00')),
        }

    supplier_ids = set(invoices_map.keys()) | set(credit_notes_map.keys())

    supplier_breakdown = []
    for supplier_id in supplier_ids:
        base = invoices_map.get(supplier_id) or credit_notes_map.get(supplier_id)
        merged = {
            'supplier': base['supplier'],
            'invoiceCount': (invoices_map.get(supplier_id) or {}).get('invoiceCount', 0),
            'totalAmount': (invoices_map.get(supplier_id) or {}).get('totalAmount', 0.0),
            'creditNoteCount': (credit_notes_map.get(supplier_id) or {}).get('creditNoteCount', 0),
            'totalCreditAmount': (credit_notes_map.get(supplier_id) or {}).get('totalCreditAmount', 0.0),
        }
        merged['netAmount'] = float(Decimal(str(merged['totalAmount'])) - Decimal(str(merged['totalCreditAmount'])))
        supplier_breakdown.append(merged)

    supplier_breakdown.sort(key=lambda x: (x.get('supplier', {}).get('name') or '').lower())

    totals_invoices_amount = invoices_qs.aggregate(total=Sum('net_to_pay'))['total'] or Decimal('0.00')
    totals_credit_notes_amount = credit_notes_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    payload = {
        'period': {
            'month': month_int,
            'year': year_int,
        },
        'totals': {
            'totalInvoicesAmount': float(totals_invoices_amount),
            'totalCreditNotesAmount': float(totals_credit_notes_amount),
            'netToPay': float(totals_invoices_amount - totals_credit_notes_amount),
            'invoicesCount': invoices_qs.count(),
            'creditNotesCount': credit_notes_qs.count(),
        },
        'supplierBreakdown': supplier_breakdown,
        'count': len(supplier_breakdown),
    }

    return Response(payload)


@extend_schema(
    summary="Résumé mensuel par fournisseur",
    description="Calculer le net mensuel exact par fournisseur : (Σ factures) - (Σ avoirs)"
)
@api_view(['GET'])
@permission_classes([IsFinanceUser])
def monthly_summary(request):
    """
    Endpoint pour le résumé mensuel par fournisseur
    Calcule: Net = (Σ net_à_payer des factures) – (Σ montant des avoirs)
    """
    month = request.query_params.get('month')
    year = request.query_params.get('year')
    supplier_id = request.query_params.get('supplier_id')
    
    # Validation des paramètres
    if not month or not year:
        return Response({
            'error': _('Les paramètres month et year sont obligatoires')
        }, status=400)
    
    try:
        month = int(month)
        year = int(year)
        if not (1 <= month <= 12):
            raise ValueError
    except ValueError:
        return Response({
            'error': _('Paramètres month et year invalides')
        }, status=400)
    
    # Base queryset pour les factures
    invoices_queryset = Invoice.objects.filter(
        month=month,
        year=year,
        is_active=True
    )
    
    # Base queryset pour les avoirs
    credit_notes_queryset = CreditNote.objects.filter(
        month=month,
        year=year,
        is_active=True
    )
    
    # Filtrer par fournisseur si spécifié
    if supplier_id:
        invoices_queryset = invoices_queryset.filter(supplier_id=supplier_id)
        credit_notes_queryset = credit_notes_queryset.filter(supplier_id=supplier_id)
    
    # Agrégation des factures par fournisseur
    invoices_summary = invoices_queryset.values(
        'supplier_id',
        'supplier__name',
        'supplier__code'
    ).annotate(
        total_invoices=Sum('net_to_pay'),
        invoice_count=Count('id')
    ).order_by('supplier__name')
    
    # Agrégation des avoirs par fournisseur
    credit_notes_summary = credit_notes_queryset.values(
        'supplier_id'
    ).annotate(
        total_credit_notes=Sum('amount'),
        credit_note_count=Count('id')
    )
    
    # Fusionner les résultats
    result = []
    for invoice_data in invoices_summary:
        supplier_id = invoice_data['supplier_id']
        
        # Trouver les avoirs correspondants
        credit_data = next(
            (cn for cn in credit_notes_summary if cn['supplier_id'] == supplier_id),
            {'total_credit_notes': Decimal('0.00'), 'credit_note_count': 0}
        )
        
        total_invoices = invoice_data['total_invoices'] or Decimal('0.00')
        total_credit_notes = credit_data['total_credit_notes'] or Decimal('0.00')
        
        result.append({
            'supplier_id': supplier_id,
            'supplier_name': invoice_data['supplier__name'],
            'supplier_code': invoice_data['supplier__code'],
            'month': month,
            'year': year,
            'total_invoices': total_invoices,
            'total_credit_notes': total_credit_notes,
            'net_amount': total_invoices - total_credit_notes,
            'invoice_count': invoice_data['invoice_count'],
            'credit_note_count': credit_data['credit_note_count']
        })
    
    # Ajouter les fournisseurs avec uniquement des avoirs
    supplier_ids_with_invoices = {item['supplier_id'] for item in result}
    for credit_data in credit_notes_summary:
        if credit_data['supplier_id'] not in supplier_ids_with_invoices:
            supplier = Supplier.objects.get(id=credit_data['supplier_id'])
            total_credit_notes = credit_data['total_credit_notes'] or Decimal('0.00')
            
            result.append({
                'supplier_id': credit_data['supplier_id'],
                'supplier_name': supplier.name,
                'supplier_code': supplier.code,
                'month': month,
                'year': year,
                'total_invoices': Decimal('0.00'),
                'total_credit_notes': total_credit_notes,
                'net_amount': -total_credit_notes,
                'invoice_count': 0,
                'credit_note_count': credit_data['credit_note_count']
            })
    
    # Trier par nom de fournisseur
    result.sort(key=lambda x: x['supplier_name'])
    
    # Calculer les totaux généraux
    total_general = {
        'total_invoices': sum(item['total_invoices'] for item in result),
        'total_credit_notes': sum(item['total_credit_notes'] for item in result),
        'net_amount': sum(item['net_amount'] for item in result),
        'invoice_count': sum(item['invoice_count'] for item in result),
        'credit_note_count': sum(item['credit_note_count'] for item in result),
        'supplier_count': len(result)
    }
    
    return Response({
        'period': {
            'month': month,
            'year': year,
            'month_name': _(f"Month {month}")
        },
        'summary': result,
        'total_general': total_general,
        'count': len(result)
    })


@extend_schema(
    summary="Requête SQL agrégée exemple",
    description="Exemple de requête SQL optimisée pour les calculs financiers"
)
@api_view(['GET'])
@permission_classes([IsFinanceUser])
def sql_example(request):
    """
    Endpoint montrant la requête SQL générée pour les calculs
    """
    from django.db import connection
    
    month = request.query_params.get('month', '1')
    year = request.query_params.get('year', '2024')
    
    # Requête SQL optimisée
    sql_query = """
    WITH invoices_summary AS (
        SELECT 
            s.id as supplier_id,
            s.name as supplier_name,
            s.code as supplier_code,
            COALESCE(SUM(i.net_to_pay), 0) as total_invoices,
            COUNT(i.id) as invoice_count
        FROM suppliers_suppliers s
        LEFT JOIN invoices_invoices i ON s.id = i.supplier_id 
            AND i.month = %s 
            AND i.year = %s 
            AND i.is_active = true
        GROUP BY s.id, s.name, s.code
    ),
    credit_notes_summary AS (
        SELECT 
            s.id as supplier_id,
            COALESCE(SUM(cn.amount), 0) as total_credit_notes,
            COUNT(cn.id) as credit_note_count
        FROM suppliers_suppliers s
        LEFT JOIN credit_notes_credit_notes cn ON s.id = cn.supplier_id 
            AND cn.month = %s 
            AND cn.year = %s 
            AND cn.is_active = true
        GROUP BY s.id
    )
    SELECT 
        COALESCE(i.supplier_id, cn.supplier_id) as supplier_id,
        COALESCE(i.supplier_name, cn.supplier_name) as supplier_name,
        COALESCE(i.supplier_code, cn.supplier_code) as supplier_code,
        %s as month,
        %s as year,
        COALESCE(i.total_invoices, 0) as total_invoices,
        COALESCE(cn.total_credit_notes, 0) as total_credit_notes,
        COALESCE(i.total_invoices, 0) - COALESCE(cn.total_credit_notes, 0) as net_amount,
        COALESCE(i.invoice_count, 0) as invoice_count,
        COALESCE(cn.credit_note_count, 0) as credit_note_count
    FROM invoices_summary i
    FULL OUTER JOIN credit_notes_summary cn ON i.supplier_id = cn.supplier_id
    WHERE COALESCE(i.total_invoices, 0) > 0 OR COALESCE(cn.total_credit_notes, 0) > 0
    ORDER BY supplier_name;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [month, year, month, year, month, year])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
    
    # Formatter les résultats
    formatted_results = []
    for row in results:
        formatted_results.append(dict(zip(columns, row)))
    
    return Response({
        'sql_query': sql_query,
        'parameters': [month, year, month, year, month, year],
        'results': formatted_results,
        'explanation': _(
            "Cette requête SQL utilise des CTE (Common Table Expressions) pour optimiser "
            "les calculs agrégés et garantir la précision des montants financiers"
        )
    })
