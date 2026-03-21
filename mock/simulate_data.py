from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from simulate_config import *

@dataclass
class StudentProfile:
    student_code: str
    student_name: str
    mobile_phone: str
    school_name: str
    grade: str
    lead_created_at: pd.Timestamp
    source_channel_canonical: str
    engagement_score: float
    purchase_affinity: float


# ----------------------------
# Helpers
# ----------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic Bronze parquet datasets.")
    parser.add_argument("--output-root", default="data/bronze", help="Bronze output root directory.")
    parser.add_argument("--students", type=int, default=2500, help="Number of unique student profiles.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()


def ensure_pyarrow() -> None:
    try:
        import pyarrow  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "pyarrow is required to write parquet files. Install with: pip install pyarrow"
        ) from exc


def weighted_choice(rng: np.random.Generator, items: list[str], probs: list[float]) -> str:
    return str(rng.choice(items, p=np.array(probs) / np.sum(probs)))


def random_name(rng: np.random.Generator) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def random_phone(rng: np.random.Generator) -> str:
    first = str(rng.choice([6, 8, 9]))
    rest = "".join(rng.choice(list("0123456789"), size=8))
    digits = f"0{first}{rest}"  # 10 digits total

    fmt = int(rng.integers(0, 6))
    if fmt == 0:
        return digits
    if fmt == 1:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    if fmt == 2:
        return f"+66 {digits[1:3]} {digits[3:6]} {digits[6:]}"
    if fmt == 3:
        return f"{digits[:3]} {digits[3:6]} {digits[6:]}"
    if fmt == 4:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return f"+66-{digits[1:3]}-{digits[3:6]}-{digits[6:]}"


def dirty_student_code(code: str, rng: np.random.Generator, p: float = 0.18) -> str | None:
    if rng.random() < 0.01:
        return None
    if rng.random() >= p:
        return code

    left = " " * int(rng.integers(0, 3))
    right = " " * int(rng.integers(0, 3))
    if left == "" and right == "":
        right = " "
    return f"{left}{code}{right}"


def maybe_dirty_channel(canonical: str, rng: np.random.Generator) -> str:
    return str(rng.choice(CHANNEL_VARIANTS[canonical]))


def maybe_dirty_event_name(canonical: str, rng: np.random.Generator) -> str:
    return str(rng.choice(EVENT_VARIANTS[canonical]))


def maybe_dirty_payment_status(bucket: str, rng: np.random.Generator) -> str:
    return str(rng.choice(PAYMENT_STATUS_VARIANTS[bucket]))


def random_timestamp_between(
    rng: np.random.Generator,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.Timestamp:
    if end <= start:
        return start
    seconds = int((end - start).total_seconds())
    offset = int(rng.integers(0, max(seconds, 1)))
    return start + pd.Timedelta(seconds=offset)


def clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


# ----------------------------
# Core generation
# ----------------------------

def generate_student_profiles(n_students: int, rng: np.random.Generator) -> list[StudentProfile]:
    channel_keys = list(CHANNEL_VARIANTS.keys())
    channel_probs = [0.28, 0.20, 0.15, 0.15, 0.12, 0.10]

    profiles: list[StudentProfile] = []

    for i in range(1, n_students + 1):
        student_code = f"STU{i:06d}"

        engagement_tier = weighted_choice(
            rng,
            items=["high", "medium", "low", "inactive"],
            probs=[0.18, 0.42, 0.28, 0.12],
        )

        if engagement_tier == "high":
            engagement_score = clip01(rng.normal(0.85, 0.08))
        elif engagement_tier == "medium":
            engagement_score = clip01(rng.normal(0.58, 0.10))
        elif engagement_tier == "low":
            engagement_score = clip01(rng.normal(0.28, 0.10))
        else:
            engagement_score = clip01(rng.normal(0.06, 0.04))

        purchase_affinity = clip01(0.15 + (engagement_score * 0.7) + rng.normal(0.0, 0.12))

        lead_created_at = NOW - pd.Timedelta(days=int(rng.integers(7, 180)))
        source_channel_canonical = weighted_choice(rng, channel_keys, channel_probs)

        school_name = str(rng.choice(SCHOOL_NAMES))
        if school_name in ADULT_INSTITUTIONS:
            grade = ADULT_GRADE
        else:
            grade = str(rng.choice(K12_GRADES))

        profiles.append(
            StudentProfile(
                student_code=student_code,
                student_name=random_name(rng),
                mobile_phone=random_phone(rng),
                school_name=school_name,
                grade=grade,
                lead_created_at=lead_created_at,
                source_channel_canonical=source_channel_canonical,
                engagement_score=engagement_score,
                purchase_affinity=purchase_affinity,
            )
        )

    return profiles


def generate_leads(profiles: list[StudentProfile], rng: np.random.Generator) -> pd.DataFrame:
    rows: list[dict] = []

    for p in profiles:
        duplicate_count = 1
        dup_roll = rng.random()
        if dup_roll < 0.22:
            duplicate_count = int(rng.integers(2, 4))
        elif dup_roll < 0.27:
            duplicate_count = 4

        earliest = p.lead_created_at - pd.Timedelta(days=int(rng.integers(0, 30)))

        for idx in range(duplicate_count):
            if idx == duplicate_count - 1:
                lead_ts = p.lead_created_at
                channel = maybe_dirty_channel(p.source_channel_canonical, rng)
                name = p.student_name
                phone = p.mobile_phone
                school_name = p.school_name
                grade = p.grade
            else:
                lead_ts = random_timestamp_between(rng, earliest, p.lead_created_at)
                channel_key = weighted_choice(
                    rng,
                    items=list(CHANNEL_VARIANTS.keys()),
                    probs=[0.26, 0.20, 0.16, 0.15, 0.13, 0.10],
                )
                channel = maybe_dirty_channel(channel_key, rng)
                name = p.student_name if rng.random() > 0.05 else f"{p.student_name} "
                phone = random_phone(rng) if rng.random() < 0.30 else p.mobile_phone
                school_name = p.school_name
                grade = p.grade

            rows.append(
                {
                    "student_code": dirty_student_code(p.student_code, rng, p=0.25),
                    "student_name": name,
                    "mobile_phone": phone,
                    "school_name": school_name,
                    "grade": grade,
                    "lead_created_at": lead_ts,
                    "source_channel": channel,
                }
            )

    invalid_count = max(5, len(profiles) // 250)
    for _ in range(invalid_count):
        rows.append(
            {
                "student_code": None,
                "student_name": random_name(rng),
                "mobile_phone": random_phone(rng),
                "school_name": str(rng.choice(SCHOOL_NAMES)),
                "grade": str(rng.choice(K12_GRADES + [ADULT_GRADE])),
                "lead_created_at": NOW - pd.Timedelta(days=int(rng.integers(1, 120))),
                "source_channel": str(rng.choice(["Facebook", "LINE", "website"])),
            }
        )

    df = pd.DataFrame(rows)
    df["lead_created_at"] = pd.to_datetime(df["lead_created_at"])
    return df.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)


def pick_subject_catalog(school_name: str) -> dict[str, list[str]]:
    if school_name in ADULT_INSTITUTIONS:
        return ADULT_SUBJECTS_AND_CHAPTERS
    return K12_SUBJECTS_AND_CHAPTERS


def generate_learning_activity(profiles: list[StudentProfile], rng: np.random.Generator) -> pd.DataFrame:
    rows: list[dict] = []

    for p in profiles:
        expected_events = 2 + int(p.engagement_score * 95) + int(max(rng.normal(0, 6), -4))
        n_events = max(0, int(rng.poisson(max(expected_events, 1))))

        if p.engagement_score < 0.08 and rng.random() < 0.65:
            n_events = int(rng.integers(0, 3))

        recent_bias = clip01(0.25 + p.engagement_score * 0.6)
        subject_catalog = pick_subject_catalog(p.school_name)
        subject_keys = list(subject_catalog.keys())

        for _ in range(n_events):
            if rng.random() < recent_bias:
                days_ago = int(rng.integers(0, 30))
            else:
                days_ago = int(rng.integers(30, 120))

            event_date = NOW - pd.Timedelta(days=days_ago)
            event_time = random_timestamp_between(
                rng,
                event_date.floor("D"),
                min(event_date.floor("D") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1), NOW),
            )

            subject = str(rng.choice(subject_keys))
            chapter = str(rng.choice(subject_catalog[subject]))
            platform = str(rng.choice(PLATFORMS))

            event_name_canonical = weighted_choice(
                rng,
                items=list(EVENT_VARIANTS.keys()),
                probs=[0.26, 0.18, 0.20, 0.10, 0.12, 0.08, 0.06],
            )

            if event_name_canonical in {"view_lesson", "watch_video", "live_class_join"}:
                duration = max(1, int(rng.normal(18 + p.engagement_score * 20, 8)))
            elif event_name_canonical in {"practice", "quiz_start", "quiz_submit"}:
                duration = max(1, int(rng.normal(8 + p.engagement_score * 10, 5)))
            else:
                duration = max(1, int(rng.normal(12 + p.engagement_score * 8, 6)))

            if rng.random() < 0.015:
                duration = -abs(duration)
            elif rng.random() < 0.01:
                duration = 0

            raw_event_time = event_time
            if rng.random() < 0.01:
                raw_event_time = None

            rows.append(
                {
                    "student_code": dirty_student_code(p.student_code, rng, p=0.18),
                    "event_time": raw_event_time,
                    "event_name": maybe_dirty_event_name(event_name_canonical, rng),
                    "subject": subject,
                    "chapter": chapter,
                    "duration_minutes": duration,
                    "platform": platform,
                }
            )

    orphan_count = max(20, len(profiles) // 40)
    for i in range(orphan_count):
        subject_catalog = ADULT_SUBJECTS_AND_CHAPTERS if rng.random() < 0.3 else K12_SUBJECTS_AND_CHAPTERS
        subject = str(rng.choice(list(subject_catalog.keys())))
        rows.append(
            {
                "student_code": dirty_student_code(f"ORPHAN{i:05d}", rng, p=0.35),
                "event_time": NOW - pd.Timedelta(days=int(rng.integers(0, 60))),
                "event_name": str(rng.choice(EVENT_VARIANTS["quiz_submit"])),
                "subject": subject,
                "chapter": str(rng.choice(subject_catalog[subject])),
                "duration_minutes": int(rng.integers(3, 15)),
                "platform": str(rng.choice(PLATFORMS)),
            }
        )

    df = pd.DataFrame(rows)
    df["event_time"] = pd.to_datetime(df["event_time"])
    return df.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)


def choose_product_for_student(
    school_name: str,
    rng: np.random.Generator,
) -> tuple[str, str, float, str, str]:
    if school_name in ADULT_INSTITUTIONS:
        filtered = [p for p in PRODUCT_CATALOG if p[4] == "adult"]
        if rng.random() < 0.08:
            filtered = PRODUCT_CATALOG
    else:
        filtered = [p for p in PRODUCT_CATALOG if p[4] == "k12"]
        if rng.random() < 0.05:
            filtered = PRODUCT_CATALOG

    idx = int(rng.integers(0, len(filtered)))
    product_name, product_type, base_amount, brand_name, audience = filtered[idx]
    return product_name, product_type, float(base_amount), brand_name, audience


def generate_sales(profiles: list[StudentProfile], rng: np.random.Generator) -> pd.DataFrame:
    rows: list[dict] = []
    order_counter = 1

    for p in profiles:
        if p.school_name in ADULT_INSTITUTIONS:
            purchase_probability = clip01(0.07 + (p.purchase_affinity * 0.68))
        else:
            purchase_probability = clip01(0.03 + (p.purchase_affinity * 0.78))

        has_paid_order = rng.random() < purchase_probability

        paid_orders = 0
        if has_paid_order:
            paid_orders = 1 + int(rng.poisson(0.4 + p.purchase_affinity * 1.8))

        failed_or_pending = 0
        if rng.random() < 0.22:
            failed_or_pending = int(rng.integers(1, 3))

        total_orders = paid_orders + failed_or_pending
        if total_orders == 0:
            continue

        order_dates = []
        for _ in range(total_orders):
            start = p.lead_created_at
            if start > NOW:
                start = NOW - pd.Timedelta(days=1)
            order_dates.append(random_timestamp_between(rng, start, NOW))
        order_dates.sort()

        for idx in range(total_orders):
            product_name, product_type, base_amount, _, _ = choose_product_for_student(p.school_name, rng)
            amount = float(base_amount + int(rng.normal(0, max(base_amount * 0.05, 50))))
            amount = max(390.0, round(amount, 2))

            if idx < paid_orders:
                status_bucket = "success"
            else:
                status_bucket = weighted_choice(rng, items=["pending", "failed"], probs=[0.45, 0.55])

            rows.append(
                {
                    "student_code": dirty_student_code(p.student_code, rng, p=0.16),
                    "order_id": f"ORD{order_counter:08d}",
                    "order_date": order_dates[idx],
                    "product_name": product_name,
                    "product_type": product_type,
                    "amount": amount,
                    "payment_status": maybe_dirty_payment_status(status_bucket, rng),
                }
            )
            order_counter += 1

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["order_date"] = pd.to_datetime(df["order_date"])

    duplicate_n = max(10, int(len(df) * 0.02))
    dup_idx = rng.choice(df.index.to_numpy(), size=min(duplicate_n, len(df)), replace=False)
    df_dups = df.loc[dup_idx].copy()

    df_dups["student_code"] = df_dups["student_code"].apply(
        lambda x: dirty_student_code(x.strip() if isinstance(x, str) else x, rng, p=0.45)
        if x is not None else None
    )
    df_dups["payment_status"] = df_dups["payment_status"].apply(
        lambda x: x if rng.random() < 0.5 else str(x).upper()
    )

    orphan_sales = []
    for i in range(max(10, len(profiles) // 100)):
        product_name, product_type, base_amount, _, _ = choose_product_for_student(
            "Skooldio" if rng.random() < 0.25 else "OnDemand",
            rng,
        )
        orphan_sales.append(
            {
                "student_code": dirty_student_code(f"ORPHAN{i:05d}", rng, p=0.25),
                "order_id": f"ORDX{i:06d}",
                "order_date": NOW - pd.Timedelta(days=int(rng.integers(0, 90))),
                "product_name": product_name,
                "product_type": product_type,
                "amount": float(base_amount),
                "payment_status": maybe_dirty_payment_status("success", rng),
            }
        )

    df = pd.concat([df, df_dups, pd.DataFrame(orphan_sales)], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)


# ----------------------------
# Write outputs
# ----------------------------

def write_parquet(df: pd.DataFrame, output_dir: Path, file_name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / file_name
    df.to_parquet(path, index=False, engine="pyarrow")
    return path


def build_manifest(
    output_root: Path,
    leads_df: pd.DataFrame,
    learning_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    seed: int,
    students: int,
) -> dict:
    def count_blank_or_null(series: pd.Series) -> int:
        s = series.astype("string").fillna("")
        return int(s.str.strip().eq("").sum())

    manifest = {
        "generated_at": NOW.isoformat(),
        "seed": seed,
        "students": students,
        "output_root": str(output_root),
        "datasets": {
            "leads": {
                "rows": int(len(leads_df)),
                "null_student_code_rows": count_blank_or_null(leads_df["student_code"]),
                "duplicate_student_code_rows_before_clean": int(
                    leads_df["student_code"]
                    .astype("string")
                    .fillna("")
                    .str.strip()
                    .duplicated(keep=False)
                    .sum()
                ),
                "school_name_distribution": leads_df["school_name"].astype("string").value_counts().head(10).to_dict(),
            },
            "learning_activity": {
                "rows": int(len(learning_df)),
                "null_student_code_rows": count_blank_or_null(learning_df["student_code"]),
                "null_event_time_rows": int(learning_df["event_time"].isna().sum()),
                "negative_duration_rows": int((learning_df["duration_minutes"] < 0).sum()),
                "subject_distribution": learning_df["subject"].astype("string").value_counts().head(10).to_dict(),
            },
            "sales": {
                "rows": int(len(sales_df)),
                "duplicate_order_id_rows_before_clean": int(
                    sales_df["order_id"].astype("string").duplicated(keep=False).sum()
                ),
                "payment_status_distribution": sales_df["payment_status"].astype("string").value_counts().to_dict(),
                "product_distribution": sales_df["product_name"].astype("string").value_counts().head(10).to_dict(),
            },
        },
        "notes": [
            "Synthetic data created because no raw input files were attached to the assignment.",
            "Student codes intentionally contain leading/trailing spaces in some rows.",
            "Leads contain duplicate student records to support latest-record logic in Silver.",
            "Learning activity contains null keys/timestamps and negative durations for data quality checks.",
            "Sales contains duplicate order_id rows and mixed payment status values for dedup/filtering logic.",
            "K12 institutions mostly generate K12 learning/sales records; adult institutions mostly generate adult-learning/product records.",
        ],
    }
    return manifest


def main() -> None:
    args = parse_args()
    ensure_pyarrow()

    rng = np.random.default_rng(args.seed)
    output_root = Path(args.output_root)

    profiles = generate_student_profiles(args.students, rng)
    leads_df = generate_leads(profiles, rng)
    learning_df = generate_learning_activity(profiles, rng)
    sales_df = generate_sales(profiles, rng)

    leads_path = write_parquet(leads_df, output_root / "leads", "raw_leads.parquet")
    learning_path = write_parquet(
        learning_df,
        output_root / "learning_activity",
        "raw_learning_activity.parquet",
    )
    sales_path = write_parquet(sales_df, output_root / "sales", "raw_sales.parquet")

    manifest = build_manifest(
        output_root=output_root,
        leads_df=leads_df,
        learning_df=learning_df,
        sales_df=sales_df,
        seed=args.seed,
        students=args.students,
    )

    manifest_path = output_root / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print("Synthetic Bronze datasets created successfully.")
    print(f"  - Leads:            {leads_path} ({len(leads_df):,} rows)")
    print(f"  - LearningActivity: {learning_path} ({len(learning_df):,} rows)")
    print(f"  - Sales:            {sales_path} ({len(sales_df):,} rows)")
    print(f"  - Manifest:         {manifest_path}")


if __name__ == "__main__":
    main()