from django.core.management.base import BaseCommand
from authentication.models import User
from ehr.models import Patient, EHRRecord, LabResult, MedicalReport
from datetime import date


class Command(BaseCommand):
    help = 'Seeds the database with fresh sample data'

    def handle(self, *args, **kwargs):

        # ── Delete old data ──
        Patient.objects.all().delete()
        self.stdout.write('✅ Old data cleared!')

        # ── Get admin user ──
        try:
            admin = User.objects.get(username='psm')
        except User.DoesNotExist:
            self.stdout.write('❌ Admin user psm not found!')
            return

        # ── Create Users ──
        # Cardiology Doctor
        if not User.objects.filter(username='cardio_doc').exists():
            User.objects.create_user(
                username='cardio_doc',
                password='Cardio@1234',
                role='doctor',
                department='cardiology',
                clearance_level=3,
                first_name='Cardio',
                last_name='Doctor',
                is_emergency_authorized=False
            )
            self.stdout.write('✅ cardio_doc created!')

        # Psychiatry Doctor
        if not User.objects.filter(username='psych_doc').exists():
            User.objects.create_user(
                username='psych_doc',
                password='Psych@1234',
                role='doctor',
                department='psychiatry',
                clearance_level=4,
                first_name='Psych',
                last_name='Doctor',
                is_emergency_authorized=False
            )
            self.stdout.write('✅ psych_doc created!')

        # Nurse
        if not User.objects.filter(username='nurse1').exists():
            User.objects.create_user(
                username='nurse1',
                password='Nurse@1234',
                role='nurse',
                department='general',
                clearance_level=1,
                first_name='Test',
                last_name='Nurse',
                is_emergency_authorized=True
            )
            self.stdout.write('✅ nurse1 created!')

        # ── Create Patients ──
        p1 = Patient.objects.create(
            patient_id='P001',
            first_name='Rahul',
            last_name='Sharma',
            date_of_birth=date(1990, 5, 15),
            blood_group='A+',
            contact_number='9876543210',
            assigned_doctor=admin
        )

        p2 = Patient.objects.create(
            patient_id='P002',
            first_name='Priya',
            last_name='Singh',
            date_of_birth=date(1985, 8, 22),
            blood_group='B+',
            contact_number='9876543211',
            assigned_doctor=admin
        )

        p3 = Patient.objects.create(
            patient_id='P003',
            first_name='Amit',
            last_name='Kumar',
            date_of_birth=date(1995, 3, 10),
            blood_group='O+',
            contact_number='9876543212',
            assigned_doctor=admin
        )

        p4 = Patient.objects.create(
            patient_id='P004',
            first_name='Sneha',
            last_name='Patel',
            date_of_birth=date(2000, 7, 18),
            blood_group='AB+',
            contact_number='9876543213',
            assigned_doctor=admin
        )

        p5 = Patient.objects.create(
            patient_id='P005',
            first_name='Vikram',
            last_name='Mehta',
            date_of_birth=date(1978, 11, 30),
            blood_group='O-',
            contact_number='9876543214',
            assigned_doctor=admin
        )

        self.stdout.write('✅ 5 Patients created!')

        # ── Create EHR Records ──
        EHRRecord.objects.create(
            patient=p1,
            record_type='general',
            sensitivity_level=1,
            diagnosis='Common cold and mild fever',
            treatment_plan='Rest, fluids and light diet',
            medications='Paracetamol 500mg twice daily',
            notes='Patient recovering well',
            required_clearance_level=1,
            required_department=None,
            patient_consent=True,
            created_by=admin
        )

        EHRRecord.objects.create(
            patient=p2,
            record_type='mental_health',
            sensitivity_level=4,
            diagnosis='Moderate depression and anxiety disorder',
            treatment_plan='Weekly therapy sessions + medication',
            medications='Sertraline 50mg daily, Alprazolam 0.25mg',
            notes='Patient responding to treatment',
            required_clearance_level=4,
            required_department='psychiatry',
            patient_consent=True,
            created_by=admin
        )

        EHRRecord.objects.create(
            patient=p3,
            record_type='emergency',
            sensitivity_level=5,
            diagnosis='Acute cardiac arrest - emergency admission',
            treatment_plan='ICU monitoring, cardiac intervention required',
            medications='Aspirin 325mg, Heparin IV, Nitroglycerin',
            notes='Critical condition - immediate attention required',
            required_clearance_level=5,
            required_department=None,
            patient_consent=True,
            created_by=admin
        )

        EHRRecord.objects.create(
            patient=p4,
            record_type='genetic',
            sensitivity_level=3,
            diagnosis='BRCA1 gene mutation detected',
            treatment_plan='Regular screening every 6 months',
            medications='No medications currently',
            notes='Family history of breast cancer',
            required_clearance_level=3,
            required_department=None,
            patient_consent=True,
            created_by=admin
        )

        EHRRecord.objects.create(
            patient=p5,
            record_type='substance',
            sensitivity_level=4,
            diagnosis='Alcohol dependency - chronic',
            treatment_plan='De-addiction program enrollment',
            medications='Naltrexone 50mg daily',
            notes='Patient agreed to rehabilitation',
            required_clearance_level=4,
            required_department=None,
            patient_consent=True,
            created_by=admin
        )

        self.stdout.write('✅ EHR Records created!')

        # ── Create Lab Results ──
        LabResult.objects.create(
            patient=p1,
            test_name='Complete Blood Count (CBC)',
            test_date=date(2024, 1, 10),
            result_value='Normal',
            normal_range='4.5-11.0',
            unit='10^9/L',
            is_abnormal=False,
            sensitivity_level=1,
            required_clearance_level=1,
            created_by=admin
        )

        LabResult.objects.create(
            patient=p2,
            test_name='Blood Sugar Fasting',
            test_date=date(2024, 1, 12),
            result_value='126',
            normal_range='70-100',
            unit='mg/dL',
            is_abnormal=True,
            remarks='High - possible diabetes',
            sensitivity_level=2,
            required_clearance_level=2,
            created_by=admin
        )

        LabResult.objects.create(
            patient=p3,
            test_name='Troponin I Cardiac',
            test_date=date(2024, 1, 15),
            result_value='2.8',
            normal_range='0-0.4',
            unit='ng/mL',
            is_abnormal=True,
            remarks='Critically high - indicates heart attack',
            sensitivity_level=5,
            required_clearance_level=5,
            created_by=admin
        )

        LabResult.objects.create(
            patient=p4,
            test_name='BRCA Gene Test',
            test_date=date(2024, 1, 18),
            result_value='Positive',
            normal_range='Negative',
            unit='',
            is_abnormal=True,
            remarks='BRCA1 mutation confirmed',
            sensitivity_level=3,
            required_clearance_level=3,
            created_by=admin
        )

        LabResult.objects.create(
            patient=p5,
            test_name='Liver Function Test',
            test_date=date(2024, 1, 20),
            result_value='ALT: 89',
            normal_range='7-56',
            unit='U/L',
            is_abnormal=True,
            remarks='Elevated - liver damage due to alcohol',
            sensitivity_level=4,
            required_clearance_level=4,
            created_by=admin
        )

        self.stdout.write(' Lab Results created!')

        # ── Create Medical Reports ──
        MedicalReport.objects.create(
            patient=p1,
            report_type='xray',
            title='Chest X-Ray Report',
            description='Routine chest X-Ray examination',
            findings='No abnormalities detected. Lungs clear.',
            sensitivity_level=1,
            required_clearance_level=1,
            created_by=admin
        )

        MedicalReport.objects.create(
            patient=p2,
            report_type='other',
            title='Psychiatric Evaluation Report',
            description='Comprehensive psychiatric evaluation',
            findings='Patient shows signs of moderate depression',
            sensitivity_level=4,
            required_clearance_level=4,
            created_by=admin
        )

        MedicalReport.objects.create(
            patient=p3,
            report_type='ecg',
            title='Emergency ECG Report',
            description='ECG during cardiac emergency admission',
            findings='ST elevation - STEMI confirmed',
            sensitivity_level=5,
            required_clearance_level=5,
            created_by=admin
        )

        MedicalReport.objects.create(
            patient=p4,
            report_type='biopsy',
            title='Genetic Biopsy Report',
            description='Tissue biopsy for genetic analysis',
            findings='BRCA1 mutation present - high risk',
            sensitivity_level=3,
            required_clearance_level=3,
            created_by=admin
        )

        MedicalReport.objects.create(
            patient=p5,
            report_type='blood_test',
            title='Alcohol Dependency Panel',
            description='Comprehensive blood test for alcohol',
            findings='Chronic alcohol dependency confirmed',
            sensitivity_level=4,
            required_clearance_level=4,
            created_by=admin
        )

        self.stdout.write('✅ Medical Reports created!')

        self.stdout.write(self.style.SUCCESS('''


Login Credentials:
──────────────────────────────────────
psm         | Admin Doctor  | Level 5
cardio_doc  | Cardio Doctor | Level 3
psych_doc   | Psych Doctor  | Level 4
nurse1      | Nurse         | Level 1
──────────────────────────────────────

Access Matrix:
P001 General     → Everyone can access
P002 Mental Health → psych_doc, psm only
P003 Emergency   → psm only
P004 Genetic     → cardio_doc, psych_doc, psm
P005 Substance   → psych_doc, psm only
        '''))