
import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="PetLove",
    page_icon="🐾",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: #FFF8F5;
}
.block-container {
    max-width: 650px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #D96C85;
}
div.stButton > button {
    border-radius: 15px;
    min-height: 45px;
}
div[data-testid="stForm"] {
    background: white;
    padding: 15px;
    border-radius: 18px;
}
</style>
""", unsafe_allow_html=True)

st.title("🐾 PetLove")
st.caption("Một mái nhà nhỏ dành cho những người yêu thú cưng 💗")

# Kết nối Supabase
try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
except Exception as e:
    supabase = None

# Menu
menu = st.radio(
    "Bạn muốn làm gì?",
    ["🏠 Trang chủ", "➕ Đăng bài"],
    horizontal=False
)

# =====================
# ĐĂNG BÀI
# =====================
if menu == "➕ Đăng bài":

    st.header("🐶 Đăng tin thú cưng")

    with st.form("pet_form", clear_on_submit=True):

        name = st.text_input("Tên bé *")

        species = st.selectbox(
            "Loài",
            ["Chó 🐶", "Mèo 🐱", "Khác 🐾"]
        )

        breed = st.text_input("Giống")

        age = st.text_input("Tuổi")

        gender = st.selectbox(
            "Giới tính",
            ["Đực", "Cái", "Chưa rõ"]
        )

        location = st.text_input("Khu vực")

        price = st.number_input(
            "Giá / phí nhận nuôi (0 = miễn phí)",
            min_value=0
        )

        description = st.text_area("Thông tin về bé")

        image_file = st.file_uploader(
            "📸 Chọn ảnh thú cưng",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False
        )

        if image_file:
            st.image(image_file, caption="Ảnh xem trước", use_container_width=True)

        submit = st.form_submit_button("💗 Đăng bài")

    if submit:

        if not supabase:
            st.error("Không kết nối được Supabase.")
        elif not name:
            st.warning("Bà nhớ nhập tên bé nha.")
        else:

            try:

                image_url = None

                # Upload ảnh vào Supabase Storage
                if image_file:

                    file_bytes = image_file.getvalue()

                    file_name = (
                        f"{datetime.now().strftime('%Y%m%d%H%M%S')}_"
                        f"{image_file.name.replace(' ', '_')}"
                    )

                    supabase.storage.from_("pet-images").upload(
                        file_name,
                        file_bytes,
                        {
                            "content-type": image_file.type,
                            "upsert": "true"
                        }
                    )

                    image_url = supabase.storage.from_(
                        "pet-images"
                    ).get_public_url(file_name)

                # Lưu bài đăng
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

                st.success("🎉 Đăng bài thành công!")

            except Exception as e:
                st.error(f"Lỗi đăng bài: {e}")

# =====================
# TRANG CHỦ
# =====================
else:

    st.header("🐾 Các bé đang tìm chủ")

    search = st.text_input("🔎 Tìm tên, giống hoặc khu vực")

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
                            st.image(
                                pet["image_url"],
                                use_container_width=True
                            )

                        st.write(f"🐶 Loài: {pet.get('species')}")
                        st.write(f"🧬 Giống: {pet.get('breed')}")
                        st.write(f"🎂 Tuổi: {pet.get('age')}")
                        st.write(f"⚧ Giới tính: {pet.get('gender')}")
                        st.write(f"📍 Khu vực: {pet.get('location')}")
                        st.write(f"💰 Giá: {pet.get('price', 0):,} VNĐ")
                        st.write(pet.get("description"))

                        st.divider()

                        st.markdown("### 💬 Bình luận")

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
                                "Bình luận",
                                key=f"content_{pet['id']}"
                            )

                            send = st.form_submit_button("Gửi bình luận")

                            if send and username and content:

                                supabase.table("comments").insert({
                                    "pet_id": pet["id"],
                                    "username": username,
                                    "content": content
                                }).execute()

                                st.success("Đã gửi bình luận 💗")
                                st.rerun()

        except Exception as e:
            st.error(f"Lỗi tải bài đăng: {e}")

    else:
        st.warning("Chưa kết nối được cơ sở dữ liệu.")
