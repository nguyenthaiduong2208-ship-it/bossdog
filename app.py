
import streamlit as st
import uuid
import os
from supabase import create_client

st.set_page_config(
    page_title="PetLove",
    page_icon="🐾",
    layout="centered"
)

# ==============================
# DARK UI
# ==============================
st.markdown("""
<style>
.stApp {
    background-color: #101116;
    color: #F3F0F7;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 700px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}

h1, h2, h3 {
    color: #F4D9FF !important;
}

p, label, span {
    color: #E8E2ED;
}

[data-testid="stSidebar"] {
    background-color: #19171F;
}

[data-testid="stWidgetLabel"] p {
    color: #E8DDF5 !important;
}

input, textarea {
    background-color: #24212C !important;
    color: white !important;
}

div[data-testid="stForm"] {
    background: #19171F;
    border: 1px solid #302B3A;
    border-radius: 18px;
    padding: 16px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #19171F;
    border-radius: 20px;
}

.stButton > button {
    background-color: #C77DFF;
    color: #17121D;
    border: none;
    border-radius: 12px;
    min-height: 44px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #D7A5FF;
    color: #17121D;
}

.stTextInput input, .stTextArea textarea {
    border-radius: 12px;
}

hr {
    border-color: #38313F;
}

[data-testid="stFileUploader"] {
    background: #211D29;
    border-radius: 15px;
    padding: 10px;
}

img {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.markdown("""
# 🐾 PetLove
### *Your pet. Your people. Your community.*
""")

st.caption("Một nơi dành cho những người yêu thú cưng 🖤")

# ==============================
# CONNECT SUPABASE
# ==============================
try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
except Exception as e:
    supabase = None

# ==============================
# NAVIGATION
# ==============================
page = st.radio(
    "Điều hướng",
    ["🏠 Khám phá", "➕ Đăng bài"],
    index=0
)

# ==============================
# CREATE POST
# ==============================
if page == "➕ Đăng bài":

    st.markdown("## ✨ Tạo bài đăng")
    st.caption("Chia sẻ một bé thú cưng với cộng đồng")

    with st.form("create_pet_post"):

        name = st.text_input("Tên thú cưng")

        species = st.selectbox(
            "Loài",
            ["Chó 🐶", "Mèo 🐱", "Khác 🐾"]
        )

        breed = st.text_input("Giống")

        age = st.text_input("Tuổi")

        gender = st.selectbox(
            "Giới tính",
            ["Đực", "Cái", "Chưa xác định"]
        )

        location = st.text_input("Khu vực")

        price = st.number_input(
            "Giá / phí nhận nuôi (VNĐ)",
            min_value=0,
            step=10000
        )

        description = st.text_area(
            "Giới thiệu về bé",
            placeholder="Tính cách, sức khỏe, nhu cầu tìm chủ..."
        )

        image_file = st.file_uploader(
            "📸 Chọn ảnh từ điện thoại",
            type=["jpg", "jpeg", "png", "webp"]
        )

        if image_file:
            st.image(image_file, caption="Ảnh của bé", use_container_width=True)

        submit = st.form_submit_button("💜 Đăng bài")

    if submit:

        if not supabase:
            st.error("Không kết nối được Supabase.")

        elif not name.strip():
            st.warning("Hãy nhập tên thú cưng.")

        else:

            try:

                image_url = None

                # UPLOAD IMAGE
                if image_file:

                    file_bytes = image_file.getvalue()

                    file_ext = os.path.splitext(
                        image_file.name
                    )[1].lower()

                    if not file_ext:
                        file_ext = ".jpg"

                    file_name = f"{uuid.uuid4().hex}{file_ext}"

                    supabase.storage.from_("pet-images").upload(
                        path=file_name,
                        file=file_bytes,
                        file_options={
                            "content-type": image_file.type,
                            "upsert": "false"
                        }
                    )

                    image_url = supabase.storage.from_(
                        "pet-images"
                    ).get_public_url(file_name)

                # INSERT DATABASE
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

                st.success("Đăng bài thành công 🖤")
                st.balloons()

            except Exception as e:
                st.error(f"Lỗi đăng bài: {e}")

# ==============================
# HOME FEED
# ==============================
else:

    st.markdown("## 🐾 Khám phá thú cưng")

    search = st.text_input(
        "🔍 Tìm kiếm",
        placeholder="Tên, giống, khu vực..."
    )

    if supabase:

        try:

            result = supabase.table("pets").select("*").order(
                "created_at",
                desc=True
            ).execute()

            pets = result.data

            if not pets:
                st.info("Chưa có bài đăng nào. Hãy là người đầu tiên đăng bài nhé 🐾")

            for pet in pets:

                keyword = search.lower().strip()

                searchable = (
                    str(pet.get("name", "")) + " " +
                    str(pet.get("species", "")) + " " +
                    str(pet.get("breed", "")) + " " +
                    str(pet.get("location", ""))
                ).lower()

                if keyword not in searchable:
                    continue

                with st.container(border=True):

                    st.markdown(f"### 🐾 {pet.get('name', 'Thú cưng')}")

                    if pet.get("image_url"):
                        st.image(
                            pet["image_url"],
                            use_container_width=True
                        )

                    st.markdown(
                        f"**Loài:** {pet.get('species', 'Chưa cập nhật')}"
                    )

                    st.markdown(
                        f"**Giống:** {pet.get('breed') or 'Chưa cập nhật'}"
                    )

                    st.markdown(
                        f"**Tuổi:** {pet.get('age') or 'Chưa cập nhật'}"
                    )

                    st.markdown(
                        f"**Giới tính:** {pet.get('gender') or 'Chưa cập nhật'}"
                    )

                    st.markdown(
                        f"**📍 Khu vực:** {pet.get('location') or 'Chưa cập nhật'}"
                    )

                    st.markdown(
                        f"**💰 Giá:** {int(pet.get('price') or 0):,} VNĐ"
                    )

                    if pet.get("description"):
                        st.write(pet["description"])

                    st.divider()

                    st.markdown("#### 💬 Bình luận")

                    comments = supabase.table("comments").select("*").eq(
                        "pet_id", pet["id"]
                    ).order("created_at").execute()

                    for c in comments.data:
                        st.markdown(
                            f"**{c['username']}**  \n{c['content']}"
                        )

                    with st.form(f"comment_{pet['id']}"):

                        username = st.text_input(
                            "Tên",
                            key=f"username_{pet['id']}"
                        )

                        content = st.text_input(
                            "Viết bình luận...",
                            key=f"comment_content_{pet['id']}"
                        )

                        send = st.form_submit_button("💬 Gửi")

                        if send and username.strip() and content.strip():

                            supabase.table("comments").insert({
                                "pet_id": pet["id"],
                                "username": username,
                                "content": content
                            }).execute()

                            st.success("Đã gửi bình luận 💜")
                            st.rerun()

        except Exception as e:
            st.error(f"Lỗi tải dữ liệu: {e}")

    else:
        st.warning("Chưa kết nối được Supabase.")
