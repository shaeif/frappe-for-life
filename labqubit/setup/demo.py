"""Starter content so the website is not empty on a fresh install.

    bench --site <site> execute labqubit.setup.demo.create_demo_content
    bench --site <site> execute labqubit.setup.demo.publish_samples   # local preview only

Services, solutions and industries describe what LabQubit offers and are published.
Anything that is a factual claim about the company (partners, clients, case studies,
testimonials, certifications, stats, job openings) is created as an UNPUBLISHED sample:
review, replace with real details, then tick "Published". `publish_samples` publishes
them anyway so the design can be previewed on a local or staging site.
"""

import frappe

SERVICES = [
	# title, title_ar, category, icon, featured, short, short_ar, features
	(
		"Enterprise Switching & Routing",
		"التحويل والتوجيه للمؤسسات",
		"Network Infrastructure",
		"network",
		1,
		"Resilient campus and core networks designed for performance, segmentation and growth.",
		"شبكات أساسية وشبكات حرم مرنة مصممة للأداء والتقسيم والنمو.",
		[
			("layers", "Core, distribution & access design"),
			("shield-check", "Segmentation with VLANs and VRFs"),
			("activity", "Telemetry and proactive monitoring"),
		],
	),
	(
		"Network Automation",
		"أتمتة الشبكات",
		"Network Infrastructure",
		"workflow",
		1,
		"Automate configuration, compliance checks and changes across your network, with fewer errors and faster rollouts.",
		"أتمتة الإعدادات وفحوصات الامتثال والتغييرات عبر شبكتك، بأخطاء أقل وتنفيذ أسرع.",
		[
			("workflow", "Automated configuration and changes"),
			("badge-check", "Compliance checks and drift detection"),
			("file-text", "Version-controlled, self-documenting network"),
		],
	),
	(
		"Wireless & Wi-Fi 7",
		"الشبكات اللاسلكية وWi-Fi 7",
		"Network Infrastructure",
		"wifi",
		0,
		"Predictive surveys, high-density Wi-Fi and seamless roaming for offices, hotels and venues.",
		"مسوحات تنبؤية وشبكات Wi-Fi عالية الكثافة وتجوال سلس للمكاتب والفنادق والمرافق.",
		[
			("radar", "Predictive and on-site RF surveys"),
			("users", "High-density guest access"),
			("key-round", "802.1X and secure onboarding"),
		],
	),
	(
		"SD-WAN & Branch Connectivity",
		"SD-WAN وربط الفروع",
		"Network Infrastructure",
		"router",
		0,
		"Application-aware WAN that connects every branch securely over any transport.",
		"شبكة واسعة تدرك التطبيقات وتربط كل فرع بأمان عبر أي وسيلة اتصال.",
		[
			("gauge", "Application-aware path selection"),
			("cloud", "Direct, secure cloud access"),
			("clock", "Zero-touch branch rollout"),
		],
	),
	(
		"Next-Generation Firewalls",
		"جدران الحماية من الجيل التالي",
		"Cybersecurity",
		"brick-wall",
		1,
		"Design, migration and hardening of next-generation firewalls with threat prevention.",
		"تصميم جدران الحماية من الجيل التالي وترحيلها وتقويتها مع منع التهديدات.",
		[
			("shield-check", "Policy design and rule-base clean-up"),
			("scan-line", "IPS, URL filtering and sandboxing"),
			("workflow", "Migration with zero business disruption"),
		],
	),
	(
		"Zero Trust & Secure Access",
		"الثقة المعدومة والوصول الآمن",
		"Cybersecurity",
		"key-round",
		0,
		"Identity-aware access for users, devices and applications, wherever they are.",
		"وصول قائم على الهوية للمستخدمين والأجهزة والتطبيقات أينما كانوا.",
		[
			("users", "ZTNA and remote access"),
			("lock", "Network access control (NAC)"),
			("eye", "Continuous posture verification"),
		],
	),
	(
		"Security Assessments & Audits",
		"تقييمات وتدقيقات الأمن",
		"Cybersecurity",
		"scan-line",
		0,
		"Vulnerability assessments, configuration audits and compliance gap analysis.",
		"تقييم الثغرات وتدقيق الإعدادات وتحليل فجوات الامتثال.",
		[
			("scan-line", "Vulnerability and configuration review"),
			("file-text", "Compliance gap analysis"),
			("badge-check", "Prioritized remediation roadmap"),
		],
	),
	(
		"Data Center Design & Build",
		"تصميم وإنشاء مراكز البيانات",
		"Data Center",
		"server",
		1,
		"Tier-aligned data center and server room design, from power and cooling to fabric.",
		"تصميم مراكز البيانات وغرف الخوادم وفق المعايير، من الطاقة والتبريد حتى البنية الشبكية.",
		[
			("server-cog", "Spine-leaf data center fabrics"),
			("zap", "Power, cooling and containment"),
			("hard-drive", "Compute and storage integration"),
		],
	),
	(
		"Virtualization & Storage",
		"المحاكاة الافتراضية والتخزين",
		"Data Center",
		"database",
		0,
		"Hyper-converged and virtualized platforms with resilient storage and backup.",
		"منصات افتراضية ومتقاربة مع تخزين ونسخ احتياطي موثوق.",
		[
			("layers", "Hyper-converged infrastructure"),
			("database", "Primary and backup storage"),
			("rocket", "Disaster recovery design"),
		],
	),
	(
		"Structured Cabling",
		"الكابلات المهيكلة",
		"Structured Cabling",
		"cable",
		1,
		"Copper and fiber cabling installed to standard, with full testing and as-built documentation.",
		"تمديد كابلات نحاسية وألياف ضوئية وفق المعايير مع اختبار كامل ووثائق تنفيذية.",
		[
			("cable", "Cat6A and fiber backbones"),
			("badge-check", "Every link tested, with test reports"),
			("file-text", "As-built drawings and labeling"),
		],
	),
	(
		"Racks, Power & Containment",
		"الخزائن والطاقة والاحتواء",
		"Structured Cabling",
		"boxes",
		0,
		"Rack layouts, PDUs, UPS and aisle containment that keep equipment cool and serviceable.",
		"تخطيط الخزائن ووحدات توزيع الطاقة وأنظمة UPS واحتواء الممرات.",
		[
			("boxes", "Rack and cable management"),
			("zap", "UPS and intelligent PDUs"),
			("gauge", "Thermal and power monitoring"),
		],
	),
	(
		"Managed Network & NOC",
		"إدارة الشبكات ومركز العمليات",
		"Managed Services",
		"activity",
		1,
		"24x7 monitoring, incident response and change management by our network operations center.",
		"مراقبة على مدار الساعة واستجابة للحوادث وإدارة للتغييرات عبر مركز عمليات الشبكة.",
		[
			("activity", "24x7 monitoring and alerting"),
			("headset", "Incident response within SLA"),
			("file-text", "Monthly service reports"),
		],
	),
	(
		"AMC & Preventive Maintenance",
		"عقود الصيانة السنوية والوقائية",
		"Managed Services",
		"wrench",
		0,
		"Annual maintenance contracts with scheduled health checks, spares and guaranteed response.",
		"عقود صيانة سنوية تشمل فحوصات دورية وقطع غيار وزمن استجابة مضمون.",
		[
			("clock", "Scheduled preventive maintenance"),
			("package", "Spare parts and RMA handling"),
			("clock", "Guaranteed response times"),
		],
	),
	(
		"Cloud Migration & Hybrid Cloud",
		"الترحيل إلى السحابة والسحابة الهجينة",
		"Cloud & Consulting",
		"cloud",
		1,
		"Plan and execute secure migrations to public, private and hybrid cloud.",
		"تخطيط وتنفيذ ترحيل آمن إلى السحابة العامة والخاصة والهجينة.",
		[
			("cloud-cog", "Landing zone and connectivity"),
			("shield-check", "Cloud security posture"),
			("workflow", "Phased, low-risk migration"),
		],
	),
	(
		"IT Strategy & Consulting",
		"استراتيجية تقنية المعلومات والاستشارات",
		"Cloud & Consulting",
		"sparkles",
		0,
		"Independent architecture reviews, roadmaps and vendor-neutral technology advice.",
		"مراجعات معمارية مستقلة وخرائط طريق ومشورة تقنية محايدة.",
		[
			("eye", "Current-state assessment"),
			("rocket", "Three-year technology roadmap"),
			("handshake", "Vendor-neutral recommendations"),
		],
	),
	(
		"Website Development",
		"تطوير المواقع الإلكترونية",
		"Web & Application Development",
		"globe",
		1,
		"Fast, secure, bilingual company websites that are easy to manage and built to win business.",
		"مواقع إلكترونية سريعة وآمنة وثنائية اللغة، سهلة الإدارة ومصممة لجذب العملاء.",
		[
			("globe", "English and Arabic, right-to-left ready"),
			("gauge", "Performance and SEO built in"),
			("shield-check", "Secure hosting and ongoing maintenance"),
		],
	),
	(
		"Web Application Development",
		"تطوير تطبيقات الويب",
		"Web & Application Development",
		"monitor-smartphone",
		1,
		"Custom web applications, portals and dashboards that streamline operations and connect your systems.",
		"تطبيقات ويب وبوابات ولوحات معلومات مخصصة تبسّط العمليات وتربط أنظمتك ببعضها.",
		[
			("layers", "Portals, dashboards and internal tools"),
			("workflow", "Integration with your existing systems"),
			("lock", "Role-based access, secure by design"),
		],
	),
	(
		"Web Application Infrastructure & Support",
		"البنية التحتية لتطبيقات الويب ودعمها",
		"Web & Application Development",
		"cloud-cog",
		0,
		"Hosting, deployment and support infrastructure for your web applications: servers or cloud, automated deployments, monitoring and backups.",
		"بنية الاستضافة والنشر والدعم لتطبيقات الويب الخاصة بك: خوادم أو سحابة، ونشر آلي، ومراقبة، ونسخ احتياطي.",
		[
			("cloud-cog", "Cloud or on-premise hosting setup"),
			("rocket", "Automated deployments (CI/CD)"),
			("activity", "Monitoring, backups and 24x7 support"),
		],
	),
]

INDUSTRIES = [
	(
		"Enterprise",
		"المؤسسات",
		"building-2",
		"Secure, scalable networks for headquarters, branches and hybrid workforces.",
		"شبكات آمنة وقابلة للتوسع للمقرات والفروع وفرق العمل الهجينة.",
		[
			"Enterprise Switching & Routing",
			"Network Automation",
			"SD-WAN & Branch Connectivity",
			"Zero Trust & Secure Access",
			"Web Application Development",
		],
	),
	(
		"Government",
		"القطاع الحكومي",
		"landmark",
		"Compliant, resilient infrastructure for ministries, authorities and public services.",
		"بنية تحتية متوافقة ومرنة للوزارات والهيئات والخدمات العامة.",
		[
			"Next-Generation Firewalls",
			"Security Assessments & Audits",
			"Data Center Design & Build",
			"Web Application Infrastructure & Support",
		],
	),
	(
		"Oil & Gas",
		"النفط والغاز",
		"fuel",
		"Rugged networks and OT security for plants, pipelines and remote sites.",
		"شبكات متينة وأمن للتقنيات التشغيلية في المصانع وخطوط الأنابيب والمواقع النائية.",
		["Next-Generation Firewalls", "Managed Network & NOC", "Structured Cabling"],
	),
	(
		"Hospitality",
		"الضيافة",
		"hotel",
		"Guest-grade Wi-Fi and secure property networks for hotels and resorts.",
		"شبكات Wi-Fi بمستوى يليق بالضيوف وشبكات آمنة للفنادق والمنتجعات.",
		["Wireless & Wi-Fi 7", "Structured Cabling", "AMC & Preventive Maintenance", "Website Development"],
	),
]

SOLUTIONS = [
	(
		"Secure Branch Transformation",
		"تحويل الفروع الآمن",
		"network",
		"One platform for WAN, security and Wi-Fi",
		"منصة واحدة للشبكة الواسعة والأمن وWi-Fi",
		"Replace legacy MPLS and branch appliances with SD-WAN, next-generation firewalls and cloud-managed Wi-Fi.",
		"استبدال MPLS التقليدية وأجهزة الفروع بحلول SD-WAN وجدران حماية حديثة وWi-Fi مُدار سحابيًا.",
		["SD-WAN & Branch Connectivity", "Next-Generation Firewalls", "Wireless & Wi-Fi 7"],
		["Enterprise", "Hospitality"],
	),
	(
		"Zero Trust Network Access",
		"الوصول الشبكي بمبدأ الثقة المعدومة",
		"key-round",
		"Verify every user and device",
		"تحقق من كل مستخدم وجهاز",
		"Move from perimeter trust to identity-based access for users, devices and applications.",
		"الانتقال من الثقة المحيطية إلى وصول قائم على الهوية للمستخدمين والأجهزة والتطبيقات.",
		["Zero Trust & Secure Access", "Security Assessments & Audits"],
		["Enterprise", "Government"],
	),
	(
		"OT & Industrial Security",
		"أمن التقنيات التشغيلية والصناعية",
		"flame",
		"Protect plants without stopping them",
		"احمِ المنشآت دون إيقافها",
		"Visibility, segmentation and monitoring for industrial control systems in oil & gas and utilities.",
		"رؤية وتقسيم ومراقبة لأنظمة التحكم الصناعية في قطاعي النفط والغاز والمرافق.",
		["Next-Generation Firewalls", "Managed Network & NOC"],
		["Oil & Gas", "Government"],
	),
	(
		"Data Center Modernization",
		"تحديث مراكز البيانات",
		"server",
		"Faster, denser, easier to run",
		"أسرع وأكثر كثافة وأسهل تشغيلًا",
		"Modern fabrics, virtualization and containment that cut power use and simplify operations.",
		"بنى شبكية حديثة ومحاكاة افتراضية واحتواء يقلل استهلاك الطاقة ويبسط التشغيل.",
		["Data Center Design & Build", "Virtualization & Storage", "Racks, Power & Containment"],
		["Enterprise", "Government"],
	),
]

# Partnership level is left empty: set it only for partnerships the vendor has confirmed.
SAMPLE_PARTNERS = [("Cisco", ""), ("Palo Alto Networks", ""), ("Fortinet", "")]

SAMPLE_CASE_STUDIES = [
	(
		"[Sample] Secure SD-WAN for a 40-site retail network",
		"Regional retail group",
		"Enterprise",
		"Replaced legacy MPLS with SD-WAN and next-generation firewalls across 40 branches.",
		[("40", "Branches migrated"), ("38%", "Lower WAN cost"), ("0", "Business-hours outages")],
		["SD-WAN & Branch Connectivity", "Next-Generation Firewalls"],
		["Secure Branch Transformation"],
	),
	(
		"[Sample] OT network segmentation for a gas processing plant",
		"Oil & gas operator",
		"Oil & Gas",
		"Segmented plant networks and added continuous OT monitoring without production downtime.",
		[("12", "Zones segmented"), ("100%", "Assets inventoried"), ("0 h", "Production downtime")],
		["Next-Generation Firewalls", "Managed Network & NOC"],
		["OT & Industrial Security"],
	),
	(
		"[Sample] Guest Wi-Fi refresh for a 600-room resort",
		"Luxury resort",
		"Hospitality",
		"Delivered high-density Wi-Fi 7 with seamless roaming across rooms, conference halls and outdoor areas.",
		[("600", "Rooms covered"), ("4.8/5", "Guest Wi-Fi rating"), ("3 weeks", "Rollout time")],
		["Wireless & Wi-Fi 7", "Structured Cabling"],
		["Secure Branch Transformation"],
	),
]

SAMPLE_TESTIMONIALS = [
	(
		"[Sample] LabQubit migrated our entire branch network without a single business-hours outage.",
		"Sample Name",
		"Head of IT Infrastructure",
		"Retail group",
	),
	(
		"[Sample] Their engineers understood both our OT constraints and our security goals.",
		"Sample Name",
		"OT Security Lead",
		"Energy company",
	),
	(
		"[Sample] Guest complaints about Wi-Fi dropped to almost zero after the refresh.",
		"Sample Name",
		"Director of IT",
		"Hospitality group",
	),
]

SAMPLE_JOBS = [
	(
		"Network Engineer (CCNP)",
		"Engineering",
		"Full-time",
		"3+ years",
		"Design, deploy and support enterprise switching, routing and SD-WAN for our clients.",
	),
	(
		"Cybersecurity Engineer",
		"Engineering",
		"Full-time",
		"4+ years",
		"Implement and harden next-generation firewalls and zero trust access solutions.",
	),
]


def create_demo_content():
	frappe.flags.in_demo = True
	_services()
	_industries()
	_solutions()
	_samples()
	frappe.db.commit()
	from labqubit.website.context import clear_website_cache

	clear_website_cache()
	print("LabQubit demo content created.")


def publish_samples():
	"""Publish the sample records and fill demo stats. For local / staging preview only."""
	for doctype in (
		"LQ Partner",
		"LQ Case Study",
		"LQ Testimonial",
		"LQ Job Opening",
		"LQ Certification",
		"Blog Post",
	):
		for name in frappe.get_all(doctype, filters={"published": 0}, pluck="name"):
			doc = frappe.get_doc(doctype, name)
			doc.published = 1
			doc.save(ignore_permissions=True)
	settings = frappe.get_single("LQ Settings")
	settings.update({"stat_projects": 250, "stat_clients": 80, "stat_uptime": 99.98, "stat_years": 12})
	settings.save(ignore_permissions=True)
	frappe.db.commit()
	print("Samples published. Remember to unpublish or replace them before going live.")


def _insert(doctype, values):
	key = values.get("title") or values.get("partner_name") or values.get("quote")
	field = "title" if "title" in values else ("partner_name" if "partner_name" in values else "quote")
	if frappe.db.exists(doctype, {field: key}):
		return
	frappe.get_doc({"doctype": doctype, **values}).insert(ignore_permissions=True)


def _services(only=None):
	for order, (title, title_ar, category, icon, featured, short, short_ar, features) in enumerate(SERVICES):
		if only and title not in only:
			continue
		_insert(
			"LQ Service",
			{
				"title": title,
				"title_ar": title_ar,
				"category": category,
				"icon": icon,
				"featured": featured,
				"published": 1,
				"display_order": order,
				"short_description": short,
				"short_description_ar": short_ar,
				"description": f"<p>{short}</p><p>Our experienced, qualified engineers handle the full lifecycle: assessment, design, "
				"implementation, documentation and ongoing support under clear SLAs.</p>",
				"description_ar": f"<p>{short_ar}</p><p>يتولى مهندسونا ذوو الخبرة والكفاءة دورة العمل كاملة: التقييم والتصميم والتنفيذ "
				"والتوثيق والدعم المستمر وفق اتفاقيات مستوى خدمة واضحة.</p>",
				"features": [{"icon": i, "title": f} for i, f in features],
			},
		)


def _industries():
	for order, (title, title_ar, icon, short, short_ar, services) in enumerate(INDUSTRIES):
		_insert(
			"LQ Industry",
			{
				"title": title,
				"title_ar": title_ar,
				"icon": icon,
				"published": 1,
				"featured": 1,
				"display_order": order,
				"short_description": short,
				"short_description_ar": short_ar,
				"description": f"<p>{short}</p>",
				"description_ar": f"<p>{short_ar}</p>",
				"services": [{"service": s} for s in services],
			},
		)
	_link_industries()


def _link_industries(only_services=None):
	"""Link industries and services both ways, adding only missing rows."""
	for title, _ar, _icon, _s, _sa, services in INDUSTRIES:
		services = [s for s in services if not only_services or s in only_services]
		if not services or not frappe.db.exists("LQ Industry", title):
			continue
		industry = frappe.get_doc("LQ Industry", title)
		missing = [s for s in services if s not in [r.service for r in industry.services]]
		if missing:
			for service in missing:
				industry.append("services", {"service": service})
			industry.save(ignore_permissions=True)
		for service in services:
			doc = frappe.get_doc("LQ Service", service)
			if title not in [r.industry for r in doc.industries]:
				doc.append("industries", {"industry": title})
				doc.save(ignore_permissions=True)


def add_new_services(titles):
	"""Add starter services introduced after a site was first seeded. Sites that started empty are left alone."""
	if not frappe.db.exists("LQ Service", {"title": "Enterprise Switching & Routing"}):
		return
	_services(only=titles)
	_link_industries(only_services=titles)


def _solutions():
	for order, (
		title,
		title_ar,
		icon,
		tagline,
		tagline_ar,
		short,
		short_ar,
		services,
		industries,
	) in enumerate(SOLUTIONS):
		_insert(
			"LQ Solution",
			{
				"title": title,
				"title_ar": title_ar,
				"icon": icon,
				"tagline": tagline,
				"tagline_ar": tagline_ar,
				"published": 1,
				"featured": 1 if order < 3 else 0,
				"display_order": order,
				"short_description": short,
				"short_description_ar": short_ar,
				"description": f"<p>{short}</p>",
				"description_ar": f"<p>{short_ar}</p>",
				"services": [{"service": s} for s in services],
				"industries": [{"industry": i} for i in industries],
			},
		)


def _samples():
	for order, (name, level) in enumerate(SAMPLE_PARTNERS):
		_insert(
			"LQ Partner",
			{"partner_name": name, "partnership_level": level, "display_order": order, "published": 0},
		)

	for title, client, industry, summary, metrics, services, solutions in SAMPLE_CASE_STUDIES:
		_insert(
			"LQ Case Study",
			{
				"title": title,
				"client_label": client,
				"industry": industry,
				"summary": summary,
				"published": 0,
				"featured": 1,
				"published_on": frappe.utils.today(),
				"challenge": "<p>Describe the client's situation and constraints.</p>",
				"solution": "<p>Describe what LabQubit designed and delivered.</p>",
				"results": "<p>Describe measurable outcomes, approved by the client.</p>",
				"metrics": [{"value": v, "label": label} for v, label in metrics],
				"services": [{"service": s} for s in services],
				"solutions": [{"solution": s} for s in solutions],
			},
		)

	for order, (quote, author, title, company) in enumerate(SAMPLE_TESTIMONIALS):
		_insert(
			"LQ Testimonial",
			{
				"quote": quote,
				"author_name": author,
				"author_title": title,
				"company": company,
				"display_order": order,
				"published": 0,
			},
		)

	for title, issuer in (
		("[Sample] ISO/IEC 27001", "Information security management"),
		("[Sample] ISO 9001", "Quality management"),
	):
		_insert("LQ Certification", {"title": title, "issuer": issuer, "published": 0})

	for title, department, employment_type, experience, summary in SAMPLE_JOBS:
		_insert(
			"LQ Job Opening",
			{
				"title": title,
				"department": department,
				"employment_type": employment_type,
				"experience": experience,
				"location": "On-site",
				"status": "Open",
				"published": 0,
				"summary": summary,
				"description": f"<p>{summary}</p>",
				"requirements": "<ul><li>Relevant vendor certification</li><li>Strong troubleshooting skills</li></ul>",
			},
		)

	_sample_blog_post()


def _sample_blog_post():
	if not frappe.db.exists("Blogger", "labqubit"):
		frappe.get_doc({"doctype": "Blogger", "short_name": "labqubit", "full_name": "LabQubit Team"}).insert(
			ignore_permissions=True
		)
	if not frappe.db.exists("Blog Category", "insights"):
		frappe.get_doc({"doctype": "Blog Category", "title": "Insights", "name": "insights"}).insert(
			ignore_permissions=True
		)
	title = "Five questions to ask before your next firewall refresh"
	if frappe.db.exists("Blog Post", {"title": title}):
		return
	frappe.get_doc(
		{
			"doctype": "Blog Post",
			"title": title,
			"blogger": "labqubit",
			"blog_category": frappe.db.get_value("Blog Category", {"title": "Insights"}, "name"),
			"published": 0,
			"blog_intro": "(Sample article) A practical checklist for planning a next-generation firewall migration.",
			"content_type": "Markdown",
			"content_md": "## 1. What does your rule base really need?\n\nStart with usage data, not the old config.\n\n"
			"## 2. Where should inspection happen?\n\nDecide which traffic needs full threat prevention.\n\n"
			"## 3. How will you cut over?\n\nPlan phased migrations with rollback points.",
		}
	).insert(ignore_permissions=True)
