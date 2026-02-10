from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import EmployeeProfile, Payroll, Attendance
from .serializers import PayrollSerializer
from django.db import transaction
from django.db.models import Sum
from datetime import datetime, date

class PayrollListApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'ADMIN':
            queryset = Payroll.objects.select_related('employee__user').all().order_by('-month')
        elif hasattr(user, 'employee_profile'):
            queryset = Payroll.objects.filter(employee=user.employee_profile).order_by('-month')
        else:
            return Response({"error": "Not authorized"}, status=403)
        
        serializer = PayrollSerializer(queryset, many=True)
        return Response(serializer.data)

class GeneratePayrollApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'ADMIN':
            return Response({"error": "Admin only"}, status=403)

        month_str = request.data.get('month') # expected 'YYYY-MM-DD' (e.g., '2023-10-01')
        if not month_str:
            return Response({"error": "Month is required (YYYY-MM-DD)"}, status=400)
            
        try:
            month_date = datetime.strptime(month_str, '%Y-%m-%d').date()
            # Normalize to first of month
            month_start = date(month_date.year, month_date.month, 1)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        employees = EmployeeProfile.objects.all()
        generated_count = 0

        with transaction.atomic():
            for emp in employees:
                # 1. Check if payroll already exists
                if Payroll.objects.filter(employee=emp, month=month_start).exists():
                    continue

                # 2. Calculate Components
                base = emp.base_salary
                commission = emp.wallet_balance # Assuming wallet accumulates just for this period or we snapshotted it. 
                # Note: Real world scenario would likely reset wallet or track commission transactions by date.
                # For this MVP, we take current wallet balance as "Unpaid Commission" to be paid out now.
                
                deductions = 0 
                # Simple logic: Deduct 100 per late arrival in this month
                late_count = Attendance.objects.filter(
                    employee=emp, 
                    date__year=month_start.year, 
                    date__month=month_start.month,
                    is_late=True
                ).count()
                deductions = late_count * 100

                total = base + commission - deductions

                # 3. Create Payroll Record
                Payroll.objects.create(
                    employee=emp,
                    month=month_start,
                    base_salary=base,
                    commission_earned=commission,
                    deductions=deductions,
                    total_salary=total,
                    status='PENDING'
                )
                
                # 4. Reset Wallet (Commission Paid Out)
                emp.wallet_balance = 0
                emp.save()
                
                generated_count += 1

        return Response({
            "status": "success", 
            "message": f"Generated payroll for {generated_count} employees for {month_start.strftime('%B %Y')}"
        })
