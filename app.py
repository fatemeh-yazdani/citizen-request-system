# -*- coding: utf-8 -*-
import streamlit as st
import json
import joblib
import os
import pandas as pd
from collections import Counter
from datetime import datetime

CATEGORY_GUIDES = {
    "پسماند": (
        "درخواست شما در دسته «پسماند» ثبت شد.\n"
        "موضوع برای بررسی و اقدام به واحد خدمات شهری ارجاع می‌شود.\n"
        "معمولاً این موارد در کوتاه‌ترین زمان ممکن رسیدگی می‌شوند."
    ),
    "معابر": (
        "درخواست شما در دسته «معابر» ثبت شد.\n"
        "موضوع برای بررسی وضعیت آسفالت، چاله یا پیاده‌رو به واحد مربوطه ارسال می‌شود.\n"
        "پس از بررسی، اقدامات لازم انجام خواهد شد."
    ),
    "روشنایی": (
        "درخواست شما در دسته «روشنایی» ثبت شد.\n"
        "موضوع خرابی یا کمبود نور برای بررسی به واحد روشنایی معابر ارجاع می‌شود.\n"
        "معمولاً این موارد در اولویت رسیدگی قرار می‌گیرند."
    ),
    "فضای سبز": (
        "درخواست شما در دسته «فضای سبز» ثبت شد.\n"
        "موضوع مربوط به درختان، چمن یا باغچه‌ها برای رسیدگی به واحد فضای سبز ارسال می‌شود.\n"
        "پس از بررسی، اقدام لازم انجام خواهد شد."
    )
}

# =========================================================
# تنظیمات صفحه
# =========================================================
st.set_page_config(
    page_title="سامانه خدمات هوشمند شهروندی",
    page_icon="🏙️",
    layout="centered"
)

FILE_NAME = "requests.json"
ADMIN_PASSWORD = "admin123"

# =========================================================
# بارگذاری مدل
# =========================================================
@st.cache_resource
def load_model():
    if not os.path.exists("model.pkl") or not os.path.exists("vectorizer.pkl"):
        st.error("فایل‌های مدل پیدا نشد. لطفاً ابتدا مدل را آموزش دهید.")
        st.stop()
    model = joblib.load("model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

try:
    model, vectorizer = load_model()
except Exception as e:
    st.error(f"خطا در بارگذاری مدل: {e}")
    st.stop()

# =========================================================
# توابع کمکی
# =========================================================
def read_requests():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_request(title, description, category, confidence):
    requests = read_requests()
    new_id = f"KZ-{10000 + len(requests) + 1}"

    requests.append({
        "id": new_id,
        "title": title,
        "description": description,
        "category": category,
        "confidence": round(float(confidence), 3),
        "status": "ثبت شده",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(requests, f, ensure_ascii=False, indent=4)

    return new_id

def predict_category(text):
    text_vector = vectorizer.transform([text])
    prediction = model.predict(text_vector)[0]
    probabilities = model.predict_proba(text_vector)[0]
    confidence = max(probabilities)
    return prediction, confidence

# =========================================================
# مدیریت وضعیت نشست
# =========================================================
if "role" not in st.session_state:
    st.session_state.role = None
if "step" not in st.session_state:
    st.session_state.step = 1
if "title" not in st.session_state:
    st.session_state.title = ""
if "description" not in st.session_state:
    st.session_state.description = ""
if "predicted" not in st.session_state:
    st.session_state.predicted = ""
if "confidence" not in st.session_state:
    st.session_state.confidence = 0.0
if "tracking_code" not in st.session_state:
    st.session_state.tracking_code = ""
if "final_category" not in st.session_state:
    st.session_state.final_category = ""

# =========================================================
# صفحه اصلی — انتخاب نقش
# =========================================================
# =========================================================
# صفحه اصلی — انتخاب نقش
# =========================================================
if st.session_state.role is None:
    st.title("🏙️ سامانه خدمات هوشمند شهروندی")
    st.markdown("### ثبت، دسته‌بندی و پیگیری درخواست‌های شهری")
    st.markdown("---")

    st.markdown("لطفاً نقش خود را انتخاب کنید:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 👤 شهروند")
        st.caption("ثبت درخواست جدید و پیگیری وضعیت")
        if st.button("ورود به پنل شهروند", use_container_width=True, type="primary"):
            st.session_state.role = "citizen"
            st.rerun()

    with col2:
        st.markdown("#### 🔐 مدیر سیستم")
        st.caption("مدیریت درخواست‌ها و مشاهده آمار")
        if st.button("ورود به پنل مدیریت", use_container_width=True):
            st.session_state.role = "admin_login"
            st.rerun()

    st.markdown("---")
    st.caption("نسخه آزمایشی | پروژه کارآموزی")
# =========================================================
# صفحه ورود مدیر
# =========================================================
elif st.session_state.role == "admin_login":
    st.title("🔐 ورود به پنل مدیریت")
    st.markdown("برای دسترسی به پنل مدیریت، رمز عبور را وارد کنید.")

    password = st.text_input("رمز عبور", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("ورود", type="primary", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("رمز عبور اشتباه است.")
    with col2:
        if st.button("بازگشت", use_container_width=True):
            st.session_state.role = None
            st.rerun()

# =========================================================
# پنل شهروند
# =========================================================
elif st.session_state.role == "citizen":
    st.title("👤 پنل شهروند")
    st.caption("ثبت درخواست شهری و پیگیری وضعیت")

    if st.button("← بازگشت به صفحه اصلی"):
        st.session_state.role = None
        st.session_state.step = 1
        st.session_state.tracking_code = ""
        st.session_state.final_category = ""
        st.rerun()

    tab_register, tab_track = st.tabs(["📝 ثبت درخواست جدید", "🔍 پیگیری درخواست"])

    # -------------------- تب ثبت درخواست --------------------
    with tab_register:
        if st.session_state.step == 1:
            st.markdown("#### اطلاعات درخواست")
            st.markdown("عنوان و توضیحات مشکل خود را وارد کنید.")

            title = st.text_input("عنوان درخواست", placeholder="مثال: خرابی چراغ خیابان")
            description = st.text_area("توضیحات درخواست", height=130, placeholder="توضیح مختصر از مشکل...")

            if st.button("ثبت و دسته‌بندی هوشمند", type="primary", use_container_width=True):
                if not title.strip() or not description.strip():
                    st.warning("لطفاً عنوان و توضیحات را کامل وارد کنید.")
                elif len(description.strip()) < 10:
                    st.warning("توضیحات خیلی کوتاه است. لطفاً توضیح بیشتری بنویسید.")
                else:
                    full_text = title + " " + description
                    predicted, confidence = predict_category(full_text)
                    st.session_state.title = title
                    st.session_state.description = description
                    st.session_state.predicted = predicted
                    st.session_state.confidence = confidence
                    st.session_state.step = 2
                    st.rerun()

        elif st.session_state.step == 2:
            st.markdown("#### بررسی دسته‌بندی پیشنهادی")

            st.write(f"**عنوان:** {st.session_state.title}")
            st.write(f"**توضیحات:** {st.session_state.description}")
            st.success(f"**دسته‌بندی پیشنهادی:** {st.session_state.predicted}")
            st.info(f"**میزان اطمینان مدل:** {st.session_state.confidence * 100:.1f}%")

            if st.session_state.confidence < 0.70:
                st.warning("⚠️ اطمینان مدل پایین است. لطفاً دسته‌بندی را با دقت بررسی کنید.")
            else:
                st.success("✅ مدل با اطمینان بالا این دسته‌بندی را پیشنهاد داده است.")

            categories = ["پسماند", "معابر", "روشنایی", "فضای سبز"]
            final_category = st.selectbox(
                "در صورت نیاز، دسته‌بندی را اصلاح کنید:",
                categories,
                index=categories.index(st.session_state.predicted)
                if st.session_state.predicted in categories else 0
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("تأیید و ثبت نهایی", type="primary", use_container_width=True):
                    code = save_request(
                        st.session_state.title,
                        st.session_state.description,
                        final_category,
                        st.session_state.confidence
                    )
                    st.session_state.tracking_code = code
                    st.session_state.final_category = final_category
                    st.session_state.step = 3
                    st.rerun()
            with col2:
                if st.button("انصراف", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.title = ""
                    st.session_state.description = ""
                    st.session_state.predicted = ""
                    st.rerun()

        elif st.session_state.step == 3:
            st.success("درخواست شما با موفقیت ثبت شد.")

            if st.session_state.tracking_code:
                st.markdown(f"### کد پیگیری: `{st.session_state.tracking_code}`")
                st.info("این کد را برای پیگیری‌های بعدی نزد خود نگه دارید.")

            guide = CATEGORY_GUIDES.get(st.session_state.final_category, "")
            if guide:
                st.markdown("#### 🤖 راهنمای سامانه")
                st.info(guide)

            if st.button("ثبت درخواست جدید", type="primary", use_container_width=True):
                st.session_state.step = 1
                st.session_state.title = ""
                st.session_state.description = ""
                st.session_state.predicted = ""
                st.session_state.confidence = 0.0
                st.session_state.tracking_code = ""
                st.session_state.final_category = ""
                st.rerun()

    # -------------------- تب پیگیری --------------------
    with tab_track:
        st.markdown("#### پیگیری وضعیت درخواست")
        st.markdown("کد پیگیری خود را وارد کنید تا وضعیت درخواست را مشاهده کنید.")

        track_code = st.text_input("کد پیگیری", placeholder="مثال: KZ-10001")

        if st.button("استعلام وضعیت", type="primary", use_container_width=True):
            if not track_code.strip():
                st.warning("لطفاً کد پیگیری را وارد کنید.")
            else:
                requests = read_requests()
                found = next((r for r in requests if r.get("id") == track_code.strip()), None)

                if found:
                    st.success("درخواست یافت شد.")
                    st.write(f"**کد پیگیری:** {found.get('id')}")
                    st.write(f"**عنوان:** {found.get('title')}")
                    st.write(f"**توضیحات:** {found.get('description')}")
                    st.write(f"**دسته‌بندی:** {found.get('category')}")
                    st.write(f"**وضعیت فعلی:** {found.get('status')}")
                    st.write(f"**تاریخ ثبت:** {found.get('created_at')}")
                else:
                    st.error("درخواستی با این کد پیگیری یافت نشد.")
# =========================================================
# پنل مدیریت
# =========================================================
elif st.session_state.role == "admin":
    st.title("🔐 پنل مدیریت")

    if st.button("← خروج از پنل مدیریت"):
        st.session_state.role = None
        st.rerun()

    tab_list, tab_stats = st.tabs(["📋 لیست درخواست‌ها", "📊 آمار"])

    # -------------------- تب لیست درخواست‌ها --------------------
    with tab_list:
        requests = read_requests()

        if not requests:
            st.info("هنوز درخواستی ثبت نشده است.")
        else:
            st.markdown("#### جستجو و فیلتر")

            # جستجو بر اساس کد پیگیری
            search_code = st.text_input("جستجو بر اساس کد پیگیری (مثال: KZ-10001)")

            # فیلتر دسته‌بندی
            categories = sorted(list(set(r.get("category", "") for r in requests)))
            selected_category = st.selectbox("فیلتر بر اساس دسته‌بندی", ["همه"] + categories)

            # فیلتر وضعیت
            status_list = sorted(list(set(r.get("status", "ثبت شده") for r in requests)))
            selected_status = st.selectbox("فیلتر بر اساس وضعیت", ["همه"] + status_list)

            # اعمال فیلترها
            filtered = requests

            if search_code.strip():
                filtered = [r for r in filtered if r.get("id", "") == search_code.strip()]

            if selected_category != "همه":
                filtered = [r for r in filtered if r.get("category") == selected_category]

            if selected_status != "همه":
                filtered = [r for r in filtered if r.get("status") == selected_status]

            st.write(f"**تعداد نتایج:** {len(filtered)}")
            st.markdown("---")

            if not filtered:
                st.warning("درخواستی با این مشخصات پیدا نشد.")
            else:
                status_options = ["ثبت شده", "در حال بررسی", "انجام شده", "رد شده"]

                for i, req in enumerate(filtered, 1):
                    req_id = req.get("id", "-")
                    title = req.get("title", "بدون عنوان")
                    category = req.get("category", "-")
                    status = req.get("status", "ثبت شده")
                    created = req.get("created_at", "-")
                    confidence = req.get("confidence", 0)

                    with st.expander(f"{i}. [{req_id}] {title}  |  {category}  |  {status}"):
                        st.write(f"**کد پیگیری:** {req_id}")
                        st.write(f"**عنوان:** {title}")
                        st.write(f"**توضیحات:** {req.get('description', '-')}")
                        st.write(f"**دسته‌بندی:** {category}")
                        st.write(f"**وضعیت فعلی:** {status}")
                        st.write(f"**میزان اطمینان مدل:** {confidence * 100:.1f}%")
                        st.write(f"**تاریخ ثبت:** {created}")

                        st.markdown("##### تغییر وضعیت")
                        new_status = st.selectbox(
                            "وضعیت جدید",
                            status_options,
                            index=status_options.index(status) if status in status_options else 0,
                            key=f"status_{i}_{req_id}"
                        )

                        if st.button("ذخیره وضعیت", key=f"save_{i}_{req_id}"):
                            all_requests = read_requests()
                            updated = False

                            for r in all_requests:
                                if req_id != "-" and r.get("id") == req_id:
                                    r["status"] = new_status
                                    updated = True
                                    break
                                if (req_id == "-" and
                                    r.get("title") == req.get("title") and
                                    r.get("description") == req.get("description")):
                                    r["status"] = new_status
                                    if not r.get("id") or r.get("id") == "-":
                                        r["id"] = f"KZ-{10000 + all_requests.index(r) + 1}"
                                    updated = True
                                    break

                            if updated:
                                with open(FILE_NAME, "w", encoding="utf-8") as f:
                                    json.dump(all_requests, f, ensure_ascii=False, indent=4)
                                st.success(f"وضعیت درخواست به «{new_status}» تغییر کرد.")
                                st.rerun()
                            else:
                                st.error("درخواست پیدا نشد.")

    # -------------------- تب آمار --------------------
    with tab_stats:
        requests = read_requests()

        if not requests:
            st.info("هنوز درخواستی ثبت نشده است.")
        else:
            st.markdown("#### خلاصه آمار سامانه")
            st.write(f"**تعداد کل درخواست‌ها:** {len(requests)}")

            # آمار بر اساس دسته‌بندی
            st.markdown("##### آمار بر اساس دسته‌بندی")
            cat_count = Counter([r.get("category", "نامشخص") for r in requests])
            df_cat = pd.DataFrame({
                "دسته‌بندی": list(cat_count.keys()),
                "تعداد": list(cat_count.values())
            })
            st.dataframe(df_cat, use_container_width=True)
            st.bar_chart(df_cat.set_index("دسته‌بندی"))

            # آمار بر اساس وضعیت
            st.markdown("##### آمار بر اساس وضعیت")
            status_count = Counter([r.get("status", "ثبت شده") for r in requests])
            df_status = pd.DataFrame({
                "وضعیت": list(status_count.keys()),
                "تعداد": list(status_count.values())
            })
            st.dataframe(df_status, use_container_width=True)
            st.bar_chart(df_status.set_index("وضعیت"))
