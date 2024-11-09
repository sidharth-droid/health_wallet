from rest_framework.views import APIView
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework.permissions import IsAuthenticated
from .forms import UserRegistrationForm, MedicalHistoryForm, PrescriptionForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MedicalHistory, Prescription, CustomUser
from .eth_interface import contract,add_health_record, get_health_record, delete_health_record, update_health_record,grant_access, revoke_access,get_access_permissions
from eth_account import Account
from django.contrib.auth import get_user_model
from django.http import HttpResponse

class ProtectedResourceView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        return Response(data={"message": "This is a protected resource"}, status=200)

def home(request):
    return render(request, 'health_wallet/home.html')
@login_required
def dashboard(request):
    return render(request,'health_wallet/dashboard.html')
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_model = get_user_model()
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            
            acct = Account.create()
            print("test:: ", acct.address)
            user.ethereum_address = acct.address  
            
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
@login_required
def profile(request):            # Generate an Ethereum address

    return render(request, 'registration/profile.html', {'user': request.user})

@login_required
def add_medical_history(request):
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            condition = form.cleaned_data['condition']
            treatment = form.cleaned_data['treatment']
            date_diagnosed = form.cleaned_data['date_diagnosed']

            record_id = add_health_record(condition, treatment)
            if record_id:
                medical_history = form.save(commit=False)
                medical_history.user = request.user
                medical_history.record_id = record_id
                medical_history.save()
                return redirect('profile')
            else:
                return render(request, 'health_wallet/add_medical_history.html', {
                    'form': form,
                    'error': "Transaction failed. Please try again."
                })
    else:
        form = MedicalHistoryForm()
    return render(request, 'health_wallet/add_medical_history.html', {'form': form})

@login_required
def view_medical_history(request):
    records = MedicalHistory.objects.filter(user=request.user)
    return render(request, 'health_wallet/view_medical_history.html', {'records': records})

@login_required
def edit_medical_history(request, pk):
    medical_history = get_object_or_404(MedicalHistory, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST, instance=medical_history)
        if form.is_valid():
            form.save()
            return redirect('medical_history_list')
    else:
        form = MedicalHistoryForm(instance=medical_history)
    return render(request, 'health_wallet/edit_medical_history.html', {'form': form})


@login_required
def delete_medical_history(request, record_id):
    medical_history = get_object_or_404(MedicalHistory, id=record_id, user=request.user)
    
    if medical_history.record_id is not None:
        try:
            # Delete from blockchain
            delete_health_record(medical_history.record_id)
            
            medical_history.delete()
            return redirect('view_medical_history')
        except Exception as e:
            print(e)
            return render(request, 'health_wallet/view_medical_history.html', {
                'error': f"Blockchain deletion failed: {e}",
                'records': MedicalHistory.objects.filter(user=request.user)
            })
    else:
        return render(request, 'health_wallet/view_medical_history.html', {
            'error': "Record ID is missing, cannot delete from blockchain.",
            'records': MedicalHistory.objects.filter(user=request.user)
        })



@login_required
def view_record_details(request, record_id):
    record = MedicalHistory.objects.get(id=record_id)
    condition, treatment_details, owner = get_health_record(record.record_id)
    return render(request, 'health_wallet/view_record_details.html', {
        'condition': condition,
        'treatment_details': treatment_details,
        'owner': owner
    })
@login_required
def add_prescription(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.user = request.user
            prescription.save()
            return redirect('prescription_list')
    else:
        form = PrescriptionForm()
    return render(request, 'health_wallet/add_prescription.html', {'form': form})

@login_required
def edit_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        if form.is_valid():
            form.save()
            return redirect('prescription_list')
    else:
        form = PrescriptionForm(instance=prescription)
    return render(request, 'health_wallet/edit_prescription.html', {'form': form})

@login_required
def delete_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk, user=request.user)
    if request.method == 'POST':
        prescription.delete()
        return redirect('prescription_list')
    return render(request, 'health_wallet/delete_prescription.html', {'prescription': prescription})
@login_required
def prescription_list(request):
    prescriptions = Prescription.objects.filter(user=request.user)  # Adjust filter as necessary
    return render(request, 'health_wallet/prescription_list.html', {'prescriptions': prescriptions})
@login_required
def update_medical_history(request, record_id):
    medical_history = get_object_or_404(MedicalHistory, pk=record_id, user=request.user)
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST, instance=medical_history)
        if form.is_valid():
            condition = form.cleaned_data['condition']
            treatment = form.cleaned_data['treatment']

            # Blockchain transaction to update record
            tx_receipt = update_health_record(medical_history.record_id, condition, treatment)
            if tx_receipt:
                form.save()  # Update local DB after blockchain success
                return redirect('view_medical_history')
            else:
                # Handle failed transaction
                return render(request, 'edit_medical_history.html', {'form': form, 'error': 'Transaction failed'})
    else:
        form = MedicalHistoryForm(instance=medical_history)
    return render(request, 'health_wallet/edit_medical_history.html', {'form': form})
def get_user_ethereum_address(username):
    # Query the user model to get the Ethereum address
    try:
        user = CustomUser.objects.get(username=username)  # Assuming you have CustomUser model
        return user.ethereum_address
    except CustomUser.DoesNotExist:
        return None  # Handle case where user is not found



@login_required
def manage_permissions(request, record_id):
    if request.method == 'POST':
        provider_username = request.POST.get('provider_username')
        if not provider_username:
            return HttpResponse("Provider username is required", status=400)

        provider_address = get_user_ethereum_address(provider_username)
        if provider_address is None:
            return HttpResponse(f"User {provider_username} not found", status=404)

        can_view = 'can_view' in request.POST
        can_edit = 'can_edit' in request.POST
        can_delete = 'can_delete' in request.POST
        is_permanent = 'is_permanent' in request.POST
        expiry_time = request.POST.get('expiry_time', '0')
        try:
            expiry_time = int(expiry_time) if expiry_time else 0
        except ValueError:
            return HttpResponse("Invalid expiry time", status=400)

        tx_receipt = grant_access(record_id, provider_address, can_view, can_edit, can_delete, is_permanent, expiry_time)
        
        if not tx_receipt:
            return HttpResponse("Failed to grant access on the blockchain", status=500)

        # Redirect to view where permissions are visible
        return redirect('view_record_permissions', record_id=record_id)

    return render(request, 'health_wallet/manage_permissions.html', {'record_id': record_id})

@login_required
def view_record_permissions(request, record_id):
    permissions = get_access_permissions(record_id, request.user.ethereum_address)

    return render(request, 'health_wallet/view_record_permissions.html', {
        'record_id': record_id,
        'permissions': [permissions] 
    })

def get_access_permissions(record_id, user_address):
    try:
        # Call the contract method and capture the permissions data
        print(f"Fetching permissions for record_id {record_id} and user_address {user_address}")

        permission_data = contract.functions.getAccessPermissions(record_id, user_address).call()

        # Check if `permission_data` is valid and structured as expected
        if permission_data and isinstance(permission_data, (list, tuple)) and len(permission_data) == 5:
            permissions = {
                'canView': permission_data[0],
                'canEdit': permission_data[1],
                'canDelete': permission_data[2],
                'isPermanent': permission_data[3],
                'expiryTime': permission_data[4]
            }
        else:
            # Return default structure if data is missing or invalid
            permissions = {
                'canView': False,
                'canEdit': False,
                'canDelete': False,
                'isPermanent': False,
                'expiryTime': 0
            }
    except Exception as e:
        print(f"Error fetching permissions: {e}")
        # Return default permissions in case of any exception
        permissions = {
            'canView': False,
            'canEdit': False,
            'canDelete': False,
            'isPermanent': False,
            'expiryTime': 0
        }

    return permissions
