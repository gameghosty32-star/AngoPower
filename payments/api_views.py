from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import Customer
from billing_app.models import Invoice
from .models import Transaction
from .services import recharge_balance, pay_invoice
from .serializers import (
    CustomerSerializer,
    InvoiceSerializer,
    TransactionSerializer,
    RechargeSerializer,
    PayInvoiceSerializer,
)


class IsCustomerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CustomerListAPI(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)


class CustomerDetailAPI(generics.RetrieveAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)


class InvoiceListAPI(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(customer__user=self.request.user)


class TransactionListAPI(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(customer__user=self.request.user)


class RechargeAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RechargeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                customer = Customer.objects.get(user=request.user)
                txn = recharge_balance(
                    customer.pk,
                    serializer.validated_data['amount'],
                )
                return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)
            except Customer.DoesNotExist:
                return Response({'error': 'No customer profile'}, status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayInvoiceAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PayInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            try:
                invoice = Invoice.objects.get(
                    pk=serializer.validated_data['invoice_id'],
                    customer__user=request.user,
                )
                txn = pay_invoice(invoice.pk, serializer.validated_data['amount'])
                return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)
            except Invoice.DoesNotExist:
                return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
