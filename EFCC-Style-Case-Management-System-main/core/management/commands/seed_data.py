"""
Management command: python manage.py seed_data

Seeds the database with realistic EFCC-style sample data:
  - 6 users (1 admin, 2 investigators, 1 legal, 1 analyst, 1 extra)
  - 10 cases with priorities and statuses
  - Evidence, comments, suspects, deadlines per case
  - Intelligence sources and reports
  - Notifications
  - Activity logs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        # Import here to avoid issues at module load time
        from core.models import (
            User, Case, Evidence, ActivityLog, CaseStatusLog,
            CaseComment, Suspect, CaseDeadline, Notification,
        )
        from intel.models import IntelligenceSource, IntelReport

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Notification.objects.all().delete()
            CaseDeadline.objects.all().delete()
            Suspect.objects.all().delete()
            CaseComment.objects.all().delete()
            CaseStatusLog.objects.all().delete()
            ActivityLog.objects.all().delete()
            Evidence.objects.all().delete()
            IntelReport.objects.all().delete()
            IntelligenceSource.objects.all().delete()
            Case.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING('Existing data cleared.'))

        now = timezone.now()

        # ── USERS ─────────────────────────────────────────────────────────────
        self.stdout.write('Creating users...')

        users_data = [
            dict(username='admin_efcc',    email='admin@efcc.gov.ng',       role='admin',        first_name='Chukwuemeka', last_name='Okafor',   is_staff=True, is_superuser=True),
            dict(username='inv_ibrahim',   email='ibrahim@efcc.gov.ng',     role='investigator', first_name='Ibrahim',     last_name='Musa'),
            dict(username='inv_adaeze',    email='adaeze@efcc.gov.ng',      role='investigator', first_name='Adaeze',      last_name='Nwosu'),
            dict(username='legal_fatima',  email='fatima@efcc.gov.ng',      role='legal',        first_name='Fatima',      last_name='Aliyu'),
            dict(username='analyst_tunde', email='tunde@efcc.gov.ng',       role='analyst',      first_name='Babatunde',   last_name='Adeleke'),
            dict(username='inv_grace',     email='grace@efcc.gov.ng',       role='investigator', first_name='Grace',       last_name='Eze'),
        ]

        created_users = {}
        for ud in users_data:
            username = ud.pop('username')
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(f'  User {username} already exists, skipping.')
            else:
                user = User.objects.create(
                    username=username,
                    password=make_password('efcc1234'),
                    **ud,
                )
            created_users[username] = user

        admin   = created_users['admin_efcc']
        inv1    = created_users['inv_ibrahim']
        inv2    = created_users['inv_adaeze']
        legal   = created_users['legal_fatima']
        analyst = created_users['analyst_tunde']
        inv3    = created_users['inv_grace']

        self.stdout.write(self.style.SUCCESS('  Users created.'))

        # ── CASES ─────────────────────────────────────────────────────────────
        self.stdout.write('Creating cases...')

        cases_data = [
            dict(
                title='Operation Clean Sweep — BDC Fraud',
                description=(
                    'Investigation into a network of Bureau de Change operators '
                    'suspected of laundering over ₦4.2 billion through fictitious '
                    'forex transactions between 2021 and 2023.'
                ),
                status='investigating', priority='critical',
                created_by=admin, assigned_to=inv1,
            ),
            dict(
                title='Ponzi Scheme — Goldlink Investment Ltd',
                description=(
                    'Goldlink Investment Ltd allegedly defrauded over 12,000 investors '
                    'of ₦1.8 billion through a pyramid investment scheme promising '
                    '40% monthly returns.'
                ),
                status='investigating', priority='high',
                created_by=admin, assigned_to=inv2,
            ),
            dict(
                title='Contract Inflation — Federal Roads Ministry',
                description=(
                    'Allegations of contract inflation and kickbacks involving '
                    'road construction contracts worth ₦6.5 billion awarded between '
                    '2020 and 2022 in the Federal Ministry of Works.'
                ),
                status='open', priority='high',
                created_by=admin, assigned_to=inv1,
            ),
            dict(
                title='Cybercrime — Romance Scam Network',
                description=(
                    'A syndicate of 23 suspects operating romance scams targeting '
                    'victims in the US, UK, and Canada. Estimated proceeds exceed $2.1M.'
                ),
                status='closed', priority='medium',
                created_by=inv1, assigned_to=inv3,
            ),
            dict(
                title='Money Laundering — Real Estate Front',
                description=(
                    'Suspected use of real estate transactions in Abuja and Lagos '
                    'to launder proceeds of advance fee fraud. Properties valued at '
                    'over ₦2.3 billion under scrutiny.'
                ),
                status='investigating', priority='critical',
                created_by=admin, assigned_to=inv2,
            ),
            dict(
                title='Tax Evasion — Apex Petroleum Ltd',
                description=(
                    'Apex Petroleum Ltd allegedly under-declared revenue by ₦900 million '
                    'over three fiscal years, evading approximately ₦270 million in taxes.'
                ),
                status='open', priority='medium',
                created_by=admin, assigned_to=inv1,
            ),
            dict(
                title='Embezzlement — State Pension Fund',
                description=(
                    'Former pension fund administrator suspected of diverting ₦520 million '
                    'from the state pension fund into personal accounts over 18 months.'
                ),
                status='investigating', priority='high',
                created_by=admin, assigned_to=inv3,
            ),
            dict(
                title='Import Duty Fraud — Apapa Port',
                description=(
                    'Syndicate allegedly colluding with customs officials to under-declare '
                    'the value of imported goods, causing revenue loss of ₦1.1 billion.'
                ),
                status='open', priority='medium',
                created_by=inv2, assigned_to=inv2,
            ),
            dict(
                title='Advance Fee Fraud — Diplomatic Scam',
                description=(
                    'Suspects impersonating foreign diplomats and UN officials to defraud '
                    'victims of funds promised as "release fees" for non-existent inheritances.'
                ),
                status='closed', priority='low',
                created_by=inv3, assigned_to=inv3,
            ),
            dict(
                title='Cryptocurrency Fraud — BitVault Exchange',
                description=(
                    'BitVault Exchange allegedly operated without a licence and misappropriated '
                    'customer funds totalling ₦3.7 billion before shutting down abruptly.'
                ),
                status='open', priority='critical',
                created_by=admin, assigned_to=inv1,
            ),
        ]

        cases = []
        for i, cd in enumerate(cases_data):
            case, created = Case.objects.get_or_create(
                title=cd['title'],
                defaults={**cd, 'created_at': now - timedelta(days=random.randint(10, 180))},
            )
            cases.append(case)
            if created:
                ActivityLog.objects.create(
                    user=cd['created_by'], case=case,
                    action='create_case', details=f'Case created: {case.title}',
                )

        self.stdout.write(self.style.SUCCESS(f'  {len(cases)} cases ready.'))

        # ── STATUS LOGS ───────────────────────────────────────────────────────
        self.stdout.write('Creating status logs...')
        for case in cases:
            if case.status in ('investigating', 'closed'):
                CaseStatusLog.objects.get_or_create(
                    case=case, previous_status='open', new_status='investigating',
                    defaults=dict(
                        changed_by=case.assigned_to or admin,
                        note='Case moved to active investigation.',
                    ),
                )
            if case.status == 'closed':
                CaseStatusLog.objects.get_or_create(
                    case=case, previous_status='investigating', new_status='closed',
                    defaults=dict(
                        changed_by=admin,
                        note='Investigation concluded. Case closed.',
                    ),
                )

        # ── SUSPECTS ──────────────────────────────────────────────────────────
        self.stdout.write('Creating suspects...')

        suspects_data = [
            dict(case=cases[0], full_name='Emeka Okonkwo', alias='The Banker',
                 nationality='Nigerian', phone='+234 803 111 2233',
                 notes='Primary suspect. Controls 7 BDC accounts.', added_by=inv1),
            dict(case=cases[0], full_name='Aisha Bello', alias='Madam Forex',
                 nationality='Nigerian', phone='+234 806 445 6677',
                 notes='Suspected money mule. Linked to 3 shell companies.', added_by=inv1),
            dict(case=cases[1], full_name='Victor Osei', alias='Mr. Returns',
                 nationality='Ghanaian', phone='+233 24 789 0011',
                 notes='Director of Goldlink. Fled to Ghana.', added_by=inv2),
            dict(case=cases[2], full_name='Alhaji Suleiman Dankwambo', alias='The Contractor',
                 nationality='Nigerian', phone='+234 802 334 5566',
                 notes='Awarded 4 inflated contracts. Owns Dankwambo Construction Ltd.', added_by=inv1),
            dict(case=cases[4], full_name='Chidi Obi', alias='Property King',
                 nationality='Nigerian', phone='+234 805 667 8899',
                 notes='Registered 12 properties in Lagos under nominee names.', added_by=inv2),
            dict(case=cases[6], full_name='Mrs. Ngozi Eze-Okafor', alias='',
                 nationality='Nigerian', phone='+234 807 223 4455',
                 notes='Former pension administrator. Diverted funds via 9 accounts.', added_by=inv3),
            dict(case=cases[9], full_name='Taiwo Adeyemi', alias='Crypto King',
                 nationality='Nigerian', phone='+234 809 556 7788',
                 notes='CEO of BitVault. Transferred ₦1.2B to Dubai accounts.', added_by=inv1),
        ]

        for sd in suspects_data:
            Suspect.objects.get_or_create(
                case=sd['case'], full_name=sd['full_name'],
                defaults=sd,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(suspects_data)} suspects ready.'))

        # ── DEADLINES ─────────────────────────────────────────────────────────
        self.stdout.write('Creating deadlines...')

        deadlines_data = [
            dict(case=cases[0], title='First Court Mention', deadline_type='court_date',
                 due_date=now + timedelta(days=14), notes='Federal High Court, Abuja — Courtroom 3', created_by=legal),
            dict(case=cases[0], title='Submit Financial Analysis Report', deadline_type='filing',
                 due_date=now + timedelta(days=7), notes='Submit to prosecution team.', created_by=inv1),
            dict(case=cases[1], title='Arraignment Hearing', deadline_type='hearing',
                 due_date=now + timedelta(days=21), notes='Victor Osei extradition pending.', created_by=legal),
            dict(case=cases[2], title='Quarterly Case Review', deadline_type='review',
                 due_date=now + timedelta(days=30), notes='Review with Director of Operations.', created_by=admin),
            dict(case=cases[4], title='Asset Freeze Order Renewal', deadline_type='filing',
                 due_date=now + timedelta(days=3), notes='Renew court order before expiry.', created_by=legal),
            dict(case=cases[4], title='Prosecution Brief Submission', deadline_type='filing',
                 due_date=now - timedelta(days=2), notes='OVERDUE — escalate immediately.', created_by=legal),
            dict(case=cases[6], title='Pension Board Hearing', deadline_type='hearing',
                 due_date=now + timedelta(days=10), notes='State Pension Board will testify.', created_by=legal),
            dict(case=cases[9], title='Freeze Crypto Wallets', deadline_type='other',
                 due_date=now + timedelta(days=1), notes='Coordinate with CBN and SEC.', created_by=admin),
        ]

        for dd in deadlines_data:
            CaseDeadline.objects.get_or_create(
                case=dd['case'], title=dd['title'],
                defaults=dd,
            )

        # Mark one as completed
        CaseDeadline.objects.filter(title='Submit Financial Analysis Report').update(is_completed=True)

        self.stdout.write(self.style.SUCCESS(f'  {len(deadlines_data)} deadlines ready.'))

        # ── COMMENTS ──────────────────────────────────────────────────────────
        self.stdout.write('Creating comments...')

        comments_data = [
            dict(case=cases[0], author=inv1,
                 body='Bank records obtained from GTBank and Access Bank. Analysing transaction patterns now.'),
            dict(case=cases[0], author=legal,
                 body='Prosecution brief is ready. Awaiting sign-off from the Director.'),
            dict(case=cases[0], author=admin,
                 body='Ensure all financial exhibits are properly labelled before the court date.'),
            dict(case=cases[1], author=inv2,
                 body='Contacted Interpol for assistance with the extradition of Victor Osei from Ghana.'),
            dict(case=cases[1], author=legal,
                 body='Arraignment date confirmed. Victims\' association has been notified.'),
            dict(case=cases[2], author=inv1,
                 body='Obtained procurement records from the ministry. Discrepancies found in 3 contracts.'),
            dict(case=cases[4], author=inv2,
                 body='Traced 4 properties in Lekki Phase 1 to shell companies linked to Chidi Obi.'),
            dict(case=cases[4], author=legal,
                 body='Asset freeze order granted by the court. Valid for 90 days.'),
            dict(case=cases[6], author=inv3,
                 body='Bank statements for 9 accounts obtained. Forensic accountant engaged.'),
            dict(case=cases[9], author=inv1,
                 body='CBN has confirmed BitVault was operating without a licence since 2021.'),
            dict(case=cases[9], author=analyst,
                 body='Blockchain analysis shows ₦1.2B moved to 3 wallets in Dubai. Report attached.'),
        ]

        for cd in comments_data:
            CaseComment.objects.get_or_create(
                case=cd['case'], author=cd['author'], body=cd['body'],
                defaults=cd,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(comments_data)} comments ready.'))

        # ── NOTIFICATIONS ─────────────────────────────────────────────────────
        self.stdout.write('Creating notifications...')

        notifs_data = [
            dict(recipient=inv1, notif_type='case_assigned',
                 message='You have been assigned to case: "Operation Clean Sweep — BDC Fraud"',
                 case=cases[0]),
            dict(recipient=inv2, notif_type='case_assigned',
                 message='You have been assigned to case: "Ponzi Scheme — Goldlink Investment Ltd"',
                 case=cases[1]),
            dict(recipient=inv1, notif_type='status_changed',
                 message='Case "Contract Inflation — Federal Roads Ministry" status changed from open to investigating',
                 case=cases[2]),
            dict(recipient=inv2, notif_type='comment_added',
                 message='admin_efcc commented on case "Money Laundering — Real Estate Front"',
                 case=cases[4]),
            dict(recipient=legal, notif_type='deadline_due',
                 message='Deadline "Asset Freeze Order Renewal" is due in 3 days',
                 case=cases[4]),
            dict(recipient=inv1, notif_type='evidence_uploaded',
                 message='New evidence uploaded to case "Cryptocurrency Fraud — BitVault Exchange"',
                 case=cases[9]),
            dict(recipient=inv3, notif_type='case_assigned',
                 message='You have been assigned to case: "Embezzlement — State Pension Fund"',
                 case=cases[6]),
        ]

        for nd in notifs_data:
            Notification.objects.get_or_create(
                recipient=nd['recipient'], message=nd['message'],
                defaults=nd,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(notifs_data)} notifications ready.'))

        # ── INTELLIGENCE SOURCES ──────────────────────────────────────────────
        self.stdout.write('Creating intelligence sources...')

        sources_data = [
            dict(name='Confidential Informant Alpha', source_type='human',
                 reliability_score=5, contact_info='Via handler only.',
                 notes='Insider at a major BDC network. Highly reliable.', added_by=analyst),
            dict(name='NFIU Financial Intelligence Unit', source_type='open',
                 reliability_score=5, contact_info='nfiu.gov.ng',
                 notes='Provides STRs and CTRs on suspicious transactions.', added_by=analyst),
            dict(name='Interpol Cyber Division', source_type='cyber',
                 reliability_score=4, contact_info='interpol-cyber@interpol.int',
                 notes='Provides cyber threat intelligence and cross-border data.', added_by=analyst),
            dict(name='Signal Intercept Unit — NIA', source_type='signal',
                 reliability_score=4, contact_info='Classified.',
                 notes='Intercepts communications of high-value targets.', added_by=analyst),
            dict(name='Open Source Monitor — Social Media', source_type='open',
                 reliability_score=3, contact_info='Internal OSINT team.',
                 notes='Monitors Twitter, Facebook, Telegram for suspect activity.', added_by=analyst),
            dict(name='Blockchain Analytics — Chainalysis', source_type='cyber',
                 reliability_score=5, contact_info='chainalysis.com',
                 notes='Traces cryptocurrency transactions across wallets.', added_by=analyst),
        ]

        created_sources = []
        for sd in sources_data:
            src, _ = IntelligenceSource.objects.get_or_create(
                name=sd['name'], defaults=sd,
            )
            created_sources.append(src)

        self.stdout.write(self.style.SUCCESS(f'  {len(created_sources)} sources ready.'))

        # ── INTEL REPORTS ─────────────────────────────────────────────────────
        self.stdout.write('Creating intel reports...')

        reports_data = [
            dict(
                case=cases[0], title='BDC Network Financial Flow Analysis',
                report_type='Incident', status='active',
                content=(
                    'Analysis of 847 transactions across 7 BDC accounts reveals a '
                    'structured layering pattern. Funds originate from 3 shell companies '
                    'registered in Seychelles and are routed through multiple accounts '
                    'before being converted to USD and transferred offshore.'
                ),
                source=created_sources[1], created_by=analyst,
                latitude=9.0579, longitude=7.4951,
            ),
            dict(
                case=cases[1], title='Goldlink Investor Victim Profile',
                report_type='Incident', status='active',
                content=(
                    'Over 12,000 victims identified across 24 states. Majority are '
                    'civil servants and retirees. Average investment: ₦150,000. '
                    'Victims recruited via WhatsApp groups and church networks.'
                ),
                source=created_sources[0], created_by=analyst,
                latitude=6.5244, longitude=3.3792,
            ),
            dict(
                case=cases[4], title='Real Estate Money Laundering — Property Map',
                report_type='Surveillance', status='active',
                content=(
                    '12 properties identified in Lekki Phase 1, Banana Island, and '
                    'Maitama Abuja. All registered under nominee names. Total estimated '
                    'value: ₦2.3 billion. Linked to 4 shell companies.'
                ),
                source=created_sources[0], created_by=analyst,
                latitude=6.4281, longitude=3.4219,
            ),
            dict(
                case=cases[9], title='BitVault Cryptocurrency Wallet Trace',
                report_type='Threat', status='active',
                content=(
                    'Blockchain analysis traced ₦1.2 billion to 3 wallets in Dubai. '
                    'Funds converted to USDT and moved through 6 intermediate wallets '
                    'before reaching final destination. Coordination with UAE authorities requested.'
                ),
                source=created_sources[5], created_by=analyst,
                latitude=25.2048, longitude=55.2708,
            ),
            dict(
                case=cases[3], title='Romance Scam Network — Communication Intercept',
                report_type='Surveillance', status='archived',
                content=(
                    'Signal intercepts confirm 23 suspects operating from 4 locations '
                    'in Lagos and Ibadan. Scripts and victim lists recovered. '
                    'Proceeds transferred via cryptocurrency and hawala networks.'
                ),
                source=created_sources[3], created_by=analyst,
                latitude=6.5244, longitude=3.3792,
            ),
            dict(
                case=cases[6], title='Pension Fund Diversion — Account Trace',
                report_type='Incident', status='active',
                content=(
                    'Forensic analysis of 9 accounts confirms ₦520 million diverted '
                    'in 47 transactions over 18 months. Funds used to purchase 3 '
                    'properties and 2 luxury vehicles.'
                ),
                source=created_sources[1], created_by=analyst,
                latitude=9.0579, longitude=7.4951,
            ),
        ]

        for rd in reports_data:
            IntelReport.objects.get_or_create(
                case=rd['case'], title=rd['title'],
                defaults=rd,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(reports_data)} intel reports ready.'))

        # ── SUMMARY ───────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('  Seed data loaded successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('  Login credentials (password: efcc1234):')
        self.stdout.write('  ┌─────────────────┬──────────────┐')
        self.stdout.write('  │ Username        │ Role         │')
        self.stdout.write('  ├─────────────────┼──────────────┤')
        self.stdout.write('  │ admin_efcc      │ Admin        │')
        self.stdout.write('  │ inv_ibrahim     │ Investigator │')
        self.stdout.write('  │ inv_adaeze      │ Investigator │')
        self.stdout.write('  │ legal_fatima    │ Legal        │')
        self.stdout.write('  │ analyst_tunde   │ Analyst      │')
        self.stdout.write('  │ inv_grace       │ Investigator │')
        self.stdout.write('  └─────────────────┴──────────────┘')
        self.stdout.write('')
