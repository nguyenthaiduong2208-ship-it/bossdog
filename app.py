
import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="PetLove",
    page_icon="🐾",
    layout="wide"
)

st.title("🐾 PetLove")
st.caption("Nơi những người yêu thú cưng kết nối")

# Kết nối Supabase
try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
except Exception:
    supabase = None

# Menu
menu = st.sidebar.radio(
    "Menu",
    ["🏠 Trang chủ", "➕ Đăng thú cưng"]
)

# =========================
# TRANG ĐĂNG THÚ CƯNG
# =========================
if menu == "➕ Đăng thú cưng":
    st.header("Đăng tin thú cưng")

    with st.form("pet_form"):
        name = st.text_input("Tên thú cưng")
        species = st.selectbox("Loài", ["Chó", "Mèo", "Khác"])
        breed = st.text_input("Giống")
        age = st.text_input("Tuổi")
        gender = st.selectbox("Giới tính", ["Đực", "Cái", "Chưa rõ"])
        location = st.text_input("Khu vực")
        price = st.number_input("Giá (0 = miễn phí)", min_value=0)
        description = st.text_area("Mô tả")
        image_url = st.text_input("Link ảnh (tạm thời)")

        submit = st.form_submit_button("Đăng bài")

    if submit:
        if not supabase:
            st.error("Chưa kết nối Supabase.")
        elif not name:
            st.warning("Vui lòng nhập tên thú cưng.")
        else:
            try:
                supabase.table("pets").insert({
                    "name": name,
                    "species": species,
                    "breed": breed,
                    "age": age,
                    "gender": gender,
                    "location": location,
                    "price": price,
                    "description": description,
                    "image_url": image_url
                }).execute()

                st.success("Đăng bài thành công 🐾")
            except Exception as e:
                st.error(f"Lỗi: {e}")

# =========================
# TRANG CHỦ
# =========================
else:
    st.header("🐶🐱 Các bé đang tìm chủ")

    search = st.text_input("🔎 Tìm theo tên, giống, khu vực")

    if supabase:
        try:
            result = supabase.table("pets").select("*").order(
                "created_at", desc=True
            ).execute()

            pets = result.data

            for pet in pets:
                keyword = search.lower()

                searchable = (
                    str(pet.get("name", "")) + " " +
                    str(pet.get("species", "")) + " " +
                    str(pet.get("breed", "")) + " " +
                    str(pet.get("location", ""))
                ).lower()

                if keyword in searchable:
                    with st.container(border=True):
                        st.subheader(f"🐾 {pet['name']}")

                        if pet.get("image_url"):
                            st.image(pet["image_url"], width=300)

                        st.write("Loài:", pet.get("species"))
                        st.write("Giống:", pet.get("breed"))
                        st.write("Tuổi:", pet.get("age"))
                        st.write("Giới tính:", pet.get("gender"))
                        st.write("Khu vực:", pet.get("location"))
                        st.write("Giá:", pet.get("price", 0))
                        st.write(pet.get("description"))

                        # Bình luận
                        st.markdown("#### 💬 Bình luận")

                        comments = supabase.table("comments").select("*").eq(
                            "pet_id", pet["id"]
                        ).order("created_at").execute()

                        for c in comments.data:
                            st.write(f"**{c['username']}**: {c['content']}")

                        with st.form(f"comment_{pet['id']}"):
                            username = st.text_input(
                                "Tên của bạn",
                                key=f"user_{pet['id']}"
                            )
                            content = st.text_input(
                                "Viết bình luận",
                                key=f"content_{pet['id']}"
                            )

                            send = st.form_submit_button("Gửi")

                            if send and username and content:
                                supabase.table("comments").insert({
                                    "pet_id": pet["id"],
                                    "username": username,
                                    "content": content
                                }).execute()

                                st.success("Đã gửi bình luận!")
                                st.rerun()

        except Exception as e:
            st.error(f"Lỗi tải dữ liệu: {e}")
    else:
        st.info("Hãy cấu hình Supabase để sử dụng PetLove.")
