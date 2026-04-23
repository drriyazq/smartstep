"""Management command: tag tasks that genuinely span multiple categories.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py apply_cross_category_tags

The Task → Tag relationship is already M2M, but the existing seeders have each
task tagged with a single category. This command adds secondary-category tags
to tasks whose skill genuinely lives in two (or rarely three) categories — e.g.
"Compose a polite email" is a digital skill AND a social skill; "Compound
interest" is financial AND cognitive.

Additions only — existing tags are preserved. Safe to re-run; `.add()` is a
no-op on an existing M2M row.
"""
from django.core.management.base import BaseCommand

from content.models import Tag, Task


# ---------------------------------------------------------------------------
# Tag lookup — same primary-tag-per-category as the seeders
# ---------------------------------------------------------------------------

TAG_FOR_CATEGORY = {
    "cognitive":  ("Reasoning",        Tag.Category.COGNITIVE),
    "social":     ("Social skills",    Tag.Category.SOCIAL),
    "household":  ("Home care",        Tag.Category.HOUSEHOLD),
    "digital":    ("Digital literacy", Tag.Category.DIGITAL),
    "navigation": ("Wayfinding",       Tag.Category.NAVIGATION),
    "financial":  ("Money basics",     Tag.Category.FINANCIAL),
}


# ---------------------------------------------------------------------------
# Curated cross-category mapping — slug → list of ADDITIONAL category keys
# to apply on top of the task's existing tag(s).
# ---------------------------------------------------------------------------

CROSS_CATEGORY_TAGS: dict[str, list[str]] = {

    # ── Digital + Social — online communication is both a digital and a social skill
    "video-call-family-age6": ["social"],
    "simple-typing-message-age7": ["social"],
    "simple-email-age9": ["social"],
    "be-kind-online-age9": ["social"],
    "video-call-etiquette": ["social"],
    "compose-polite-email-age10": ["social"],
    "social-write-formal-email": ["digital"],
    "online-stranger-safety-age11": ["digital"],
    "recognize-cyberbullying-age11": ["social"],
    "group-chat-etiquette-age12": ["digital"],
    "online-gaming-etiquette-age12": ["social"],
    "setup-social-account-age13": ["social"],
    "manage-online-relationships-age15": ["digital"],
    "intentional-social-media-age16": ["digital"],
    "professional-digital-communication-age16": ["social"],
    "adult-linkedin-that-works": ["social"],

    # ── Digital + Cognitive — critical thinking applied online
    "recognize-ad-banner": ["cognitive"],
    "spot-ad-vs-content": ["cognitive"],
    "close-suspicious-popup": ["cognitive"],
    "evaluate-source-credibility": ["cognitive"],
    "spot-phishing-link": ["cognitive"],
    "algorithm-awareness-age11": ["cognitive"],
    "fact-check-simple-age11": ["cognitive"],
    "recognize-ai-generated-media": ["cognitive"],
    "spot-phishing-age12": ["cognitive"],
    "notification-hygiene-age13": ["cognitive"],
    "set-screen-time-limits-age13": ["cognitive"],
    "digital-footprint-awareness": ["cognitive"],
    "digital-footprint-age14": ["cognitive"],
    "identify-misinformation-age14": ["cognitive"],
    "ai-assistant-verify-age14": ["cognitive"],
    "read-terms-basics-age14": ["cognitive"],
    "build-simple-project-age14": ["cognitive"],
    "ai-tools-critically-age15": ["cognitive"],
    "ethical-ai-use-age15": ["cognitive"],
    "spreadsheet-real-use-age15": ["cognitive"],
    "spot-phishing-scam-age15": ["cognitive"],
    "manage-screen-wellbeing-age15": ["cognitive"],
    "build-cv-online-age15": ["cognitive"],
    "evaluate-online-source-age16": ["cognitive"],
    "audit-online-presence-age16": ["cognitive"],
    "digital-productivity-system-age16": ["cognitive"],
    "know-your-data-age16": ["cognitive"],
    "common-cyber-attacks-age16": ["cognitive"],
    "adult-use-ai-properly": ["cognitive"],
    "adult-spreadsheet-mastery": ["cognitive"],
    "adult-productivity-system": ["cognitive"],
    "adult-fact-check-discipline": ["digital"],
    "adult-manage-info-overload": ["digital"],
    "adult-digital-footprint-audit": ["cognitive"],

    # ── Digital + Financial — online money handling
    "digital-payment-awareness-age9": ["digital"],
    "online-shopping-compare-age11": ["digital"],
    "subscription-hidden-costs-age11": ["digital"],
    "manage-subscriptions-age15": ["digital"],
    "adult-secure-online-banking": ["financial"],

    # ── Financial + Cognitive — reasoning about money
    "needs-vs-wants-age6": ["cognitive"],
    "check-change": ["cognitive"],
    "count-change": ["cognitive"],
    "compare-prices": ["cognitive"],
    "wants-vs-needs-age9": ["cognitive"],
    "read-receipt": ["cognitive"],
    "recognize-scam-offer": ["cognitive"],
    "calculate-simple-discount": ["cognitive"],
    "compare-unit-prices-age10": ["cognitive"],
    "compare-unit-prices": ["cognitive"],
    "estimate-grocery-total": ["cognitive"],
    "plan-weekly-budget": ["cognitive"],
    "spending-diary-week-age11": ["cognitive"],
    "understand-family-budget-age12": ["cognitive"],
    "monthly-allowance-budget-age12": ["cognitive"],
    "compound-interest-basics-age13": ["cognitive"],
    "digital-vs-cash-awareness-age13": ["cognitive"],
    "track-week-own-spending-age13": ["cognitive"],
    "create-monthly-budget-age14": ["cognitive"],
    "opportunity-cost-age14": ["cognitive"],
    "understand-interest-age14": ["cognitive"],
    "track-spending-month-age14": ["cognitive"],
    "invest-basics-age15": ["cognitive"],
    "emergency-fund-plan-age15": ["cognitive"],
    "compare-financial-products-age15": ["cognitive"],
    "read-payslip-age15": ["cognitive"],
    "read-payslip-tax-age15": ["cognitive"],
    "budget-large-purchase-age16": ["cognitive"],
    "earn-and-manage-income-age16": ["cognitive"],
    "simple-tax-declaration-age16": ["cognitive"],
    "tax-return-basics-age16": ["cognitive"],
    "understand-credit-score-age16": ["cognitive"],
    "understand-emi-loans-age16": ["cognitive"],
    "understand-insurance-age16": ["cognitive"],
    "adult-avoid-lifestyle-creep": ["cognitive"],
    "adult-credit-card-discipline": ["cognitive"],
    "adult-emergency-fund-6mo": ["cognitive"],
    "adult-health-insurance-real": ["cognitive"],
    "adult-term-life-insurance": ["cognitive"],
    "adult-home-loan-math": ["cognitive"],
    "adult-tax-saving-strategy": ["cognitive"],
    "adult-start-sip-index": ["cognitive"],
    "adult-read-payslip": ["cognitive"],

    # ── Financial + Social — commerce, negotiation, giving
    "shop-roleplay-age5": ["social"],
    "pay-at-shop-age6": ["social"],
    "pay-at-till-count-change-age7": ["social"],
    "donate-small-amount": ["social"],
    "social-order-restaurant": ["financial"],
    "first-paid-chore-age12": ["social"],
    "earn-outside-home-age14": ["social"],
    "negotiate-price-age15": ["social"],
    "adult-negotiate-salary": ["social"],
    "adult-manage-parent-finances": ["social"],

    # ── Cognitive + Social — reasoning applied to human interaction
    "listen-till-finished-age5": ["social"],
    "ask-teacher-help-age6": ["cognitive"],
    "manage-emotions-calm-down": ["social"],
    "social-listen-no-interrupt": ["cognitive"],
    "social-ask-help-adult": ["cognitive"],
    "accept-feedback-calmly": ["social"],
    "resolve-disagreement-words": ["social"],
    "handle-peer-pressure": ["social"],
    "ask-clarifying-question": ["social"],
    "teach-younger-kid-skill": ["social"],
    "plan-and-host-event": ["social"],
    "structured-debate-age13": ["social"],
    "critical-thinking-argument-age14": ["social"],
    "adult-public-speaking": ["social"],

    # ── Cognitive + Household — structure applied to daily routines
    "put-things-back-age5": ["household"],
    "morning-routine-age6": ["household"],
    "tidy-before-leaving-age6": ["household"],
    "sort-recycle-age6": ["household"],
    "follow-simple-recipe-age7": ["household"],
    "first-aid-small-cut": ["household"],
    "pack-lunchbox": ["cognitive"],
    "read-simple-recipe-age9": ["cognitive"],
    "home-alone-safely": ["household"],
    "plan-meals-few-days-age13": ["cognitive"],
    "manage-own-health-routine-age13": ["cognitive"],
    "manage-own-schedule-age14": ["cognitive"],

    # ── Cognitive / Navigation — emergencies are both planning and wayfinding
    "fire-escape-plan": ["navigation"],
    "call-for-help-emergency": ["navigation"],

    # ── Navigation + Cognitive — trip planning
    "plan-route-with-stops": ["cognitive"],
    "handle-transit-disruption-age11": ["cognitive"],
    "day-trip-unfamiliar-area-age14": ["cognitive"],
    "plan-trip-independently-age14": ["cognitive"],
    "read-official-document-age14": ["cognitive"],
    "lost-phone-wallet-plan-age15": ["cognitive"],
    "read-contract-before-signing-age15": ["cognitive"],
    "know-legal-rights-age15": ["cognitive"],
    "overnight-trip-solo-age16": ["cognitive"],
    "navigate-college-admission-age16": ["cognitive"],
    "travel-abroad-basics-age16": ["cognitive"],
    "understand-renting-age16": ["cognitive", "financial"],
    "adult-emergency-playbook": ["cognitive"],

    # ── Navigation + Digital — online travel and logistics
    "use-phone-maps-app": ["digital"],
    "online-travel-booking-age14": ["digital"],
    "full-job-application-age16": ["digital"],
    "adult-book-domestic-travel": ["digital"],

    # ── Navigation + Social — stranger safety and officialdom
    "shout-parent-name-if-lost-age5": ["social"],
    "trusted-adults-age6": ["social"],
    "tell-adult-stranger-age6": ["social"],
    "stranger-safety-basics": ["social"],
    "stranger-approaches-age7": ["social"],
    "interview-for-opportunity-age15": ["social"],
    "if-stopped-by-police-age15": ["social"],
    "access-mental-health-support-age16": ["social"],
    "adult-file-consumer-complaint": ["social"],
    "adult-file-fir": ["social"],
    "adult-handle-corrupt-officials": ["social"],
    "adult-stopped-by-police": ["social"],

    # ── Household + Financial — budget-aware home management
    "help-grocery-age10": ["financial"],
    "weekly-grocery-budget-age14": ["financial"],
    "grocery-shop-alone-age14": ["financial"],
    "plan-week-meals-budget-age15": ["financial"],
    "handle-utility-bill-age15": ["financial"],
    "household-budget-week-age16": ["financial"],
    "manage-home-solo-age16": ["financial"],
    "monthly-household-admin-age16": ["financial"],
    "moving-out-setup-age16": ["financial"],
    "adult-subscription-audit": ["financial"],
    "adult-week-meal-plan-budget": ["financial"],
    "adult-deal-with-landlord": ["social"],
    "adult-manage-house-help": ["social"],

    # ── Household + Navigation — emergencies at home and in the world
    "handle-emergency-alone-age14": ["household"],
    "basic-first-aid-age15": ["household"],
    "handle-home-emergency-age16": ["navigation"],
    "home-first-aid-age12": ["cognitive"],

    # ── Triple-category — tasks that genuinely span three skills
    "adult-spot-advanced-scams": ["financial", "cognitive"],
    "adult-identity-theft-response": ["financial", "cognitive"],
}


class Command(BaseCommand):
    help = (
        "Apply secondary-category tags to tasks whose skill genuinely spans "
        "more than one category. Additive; idempotent."
    )

    def handle(self, *args, **options):
        # Resolve the primary tag for each category up-front
        tag_by_category: dict[str, Tag] = {}
        for cat_key, (tag_name, tag_cat) in TAG_FOR_CATEGORY.items():
            tag, _ = Tag.objects.get_or_create(
                name=tag_name, defaults={"category": tag_cat}
            )
            tag_by_category[cat_key] = tag

        tags_added = 0
        tasks_touched = 0
        already_had = 0
        missing: list[str] = []

        for slug, secondary_cats in CROSS_CATEGORY_TAGS.items():
            task = Task.objects.filter(slug=slug).first()
            if not task:
                missing.append(slug)
                continue

            existing_cat_ids = {t.category for t in task.tags.all()}
            added_for_this_task = 0
            for cat_key in secondary_cats:
                if cat_key in existing_cat_ids:
                    already_had += 1
                    continue
                task.tags.add(tag_by_category[cat_key])
                tags_added += 1
                added_for_this_task += 1
            if added_for_this_task:
                tasks_touched += 1

        self.stdout.write(
            f"Tasks touched: {tasks_touched} / {len(CROSS_CATEGORY_TAGS)}"
        )
        self.stdout.write(f"Secondary tags added: {tags_added}")
        self.stdout.write(f"Already had the tag: {already_had}")
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    f"Missing slugs ({len(missing)}): {', '.join(missing[:10])}"
                    + ("..." if len(missing) > 10 else "")
                )
            )

        # Distribution of multi-tag tasks after the pass
        from collections import Counter
        tag_counts_per_task = Counter()
        for t in Task.objects.filter(status="approved").prefetch_related("tags"):
            cat_count = len({tg.category for tg in t.tags.all()})
            tag_counts_per_task[cat_count] += 1
        self.stdout.write("\nCategory-count distribution across approved tasks:")
        for count in sorted(tag_counts_per_task):
            label = {1: "single-category", 2: "dual-category", 3: "triple-category"}.get(
                count, f"{count}-category"
            )
            self.stdout.write(f"  {label:<18} {tag_counts_per_task[count]:>4}")

        self.stdout.write(self.style.SUCCESS("apply_cross_category_tags complete."))
