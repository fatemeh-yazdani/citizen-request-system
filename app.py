# -*- coding: utf-8 -*-
import streamlit as st
import json
import joblib
import os
import pandas as pd
from collections import Counter
from datetime import datetime

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

# =========================================================
# صفحه اصلی — انتخاب نقش
# =========================================================
if st.session_state.role is None:
    st.title("🏙️ سامانه خدمات هوشمند شهروندی")
    st.markdown("### به سامانه ثبت و پیگیری درخواست‌های شهری خوش آمدید")
    st.markdown("---")
    st.markdown("لطفاً نقش خود را انتخاب کنید:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👤 ورود شهروند", use_container_width=True, type="primary"):
            st.session_state.role = "citizen"
            st.rerun()

    with col2:
        if st.button("🔐 ورود مدیر", use_container_width=True):
            st.session_state.role = "admin_login"
            st.rerun()

    st.markdown("---")
    st.caption("این سامانه به صورت آزمایشی و در قالب پروژه کارآموزی توسعه یافته است.")

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

    if st.button("← بازگشت به صفحه اصلی"):
        st.session_state.role = None
        st.session_state.step = 1
        st.session_state.tracking_code = ""
        st.rerun()

    tab_register, tab_track = st.tabs(["📝 ثبت درخواست جدید", "🔍 پیگیری درخواست"])

    # ----- تب ثبت درخواست -----
    with tab_register:
        if st.session_state.step == 1:
            st.markdown("#### اطلاعات درخواست خود را وارد کنید")
            title = st.text_input("عنوان درخواست")
            description = st.text_area("توضیحات درخواست", height=120)

            if st.button("ثبت و دسته‌بندی هوشمند", type="primary"):
                if not title.strip() or not description.strip():
                    st.warning("لطفاً عنوان و توضیحات را کامل وارد کنید.")
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
            st.success(f"دسته‌بندی پیشنهادی مدل: **{st.session_state.predicted}**")
            st.info(f"میزان اطمینان مدل: **{st.session_state.confidence * 100:.1f}%**")

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
            st.markdown(f"### کد پیگیری: `{st.session_state.tracking_code}`")
            st.info("لطفاً این کد را برای پیگیری‌های بعدی ذخیره کنید.")

            if st.button("ثبت درخواست جدید", type="primary"):
                st.session_state.step = 1
                st.session_state.title = ""
                st.session_state.description = ""
                st.session_state.predicted = ""
                st.session_state.tracking_code = ""
                st.rerun()

    # ----- تب پیگیری -----
    with tab_track:
        st.markdown("#### پیگیری وضعیت درخواست")
        st.markdown("کد پیگیری دریافتی هنگام ثبت درخواست را وارد کنید.")

        track_code = st.text_input("کد پیگیری (مثال: KZ-10001)")

        if st.button("استعلام وضعیت", type="primary"):
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

    # ----- تب لیست -----
    with tab_list:
        requests = read_requests()

        if not requests:
            st.info("هنوز درخواستی ثبت نشده است.")
        else:
            categories = sorted(list(set(r.get("category", "") for r in requests)))
            selected = st.selectbox("فیلتر بر اساس دسته‌بندی", ["همه"] + categories)

            filtered = requests if selected == "همه" else [r for r in requests if r.get("category") == selected]
            st.write(f"**تعداد درخواست‌ها:** {len(filtered)}")

            status_options = ["ثبت شده", "در حال بررسی", "انجام شده", "رد شده"]

            for i, req in enumerate(filtered, 1):
                req_id = req.get("id", "-")
                title = req.get("title", "بدون عنوان")
                category = req.get("category", "-")
                status = req.get("status", "ثبت شده")
                created = req.get("created_at", "-")
                confidence = req.get("confidence", 0)

                with st.expander(f"{i}. [{req_id}] {title} — {category} | {status}"):
                    st.write(f"**توضیحات:** {req.get('description', '-')}")
                    st.write(f"**دسته‌بندی:** {category}")
                    st.write(f"**میزان اطمینان مدل:** {confidence * 100:.1f}%")
                    st.write(f"**تاریخ ثبت:** {created}")

                    new_status = st.selectbox(
                        "تغییر وضعیت",
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
                            st.success(f"وضعیت به «{new_status}» تغییر کرد.")
                            st.rerun()
                        else:
                            st.error("درخواست پیدا نشد.")

    # ----- تب آمار -----
    with tab_stats:
        requests = read_requests()

        if not requests:
            st.info("هنوز درخواستی ثبت نشده است.")
        else:
            st.markdown("#### خلاصه آمار درخواست‌ها")
            st.write(f"**تعداد کل درخواست‌ها:** {len(requests)}")

            categories_list = [r.get("category", "نامشخص") for r in requests]
            count = Counter(categories_list)

            df_stats = pd.DataFrame({
                "دسته‌بندی": list(count.keys()),
                "تعداد": list(count.values())
            })

            st.markdown("##### تعداد درخواست‌ها بر اساس دسته‌بندی")
            st.dataframe(df_stats, use_container_width=True)
            st.bar_chart(df_stats.set_index("دسته‌بندی"))