"""منصة ربط النماذج — عرض وإدارة الروابط (متسق مع منطق Store AliJaddi)."""
import streamlit as st

from auth_model.auth import AuthManager


def show_linking_ui():
    if not st.session_state.get("logged_in"):
        st.warning("سجّل الدخول أولاً")
        return
    st.title("🔗 منصة الربط")
    st.caption("النماذج المرتبطة بحسابك. يمكنك إلغاء الربط من هنا أو إضافة نماذج من «الحساب → النماذج».")
    auth = AuthManager()
    user = st.session_state.user
    linked = auth.get_user_models(user)
    if not linked:
        st.info("لا توجد نماذج مرتبطة. افتح «الحساب» ومن تبويب «النماذج» اربط نموذجاً.")
        return
    for mid, info in sorted(linked.items(), key=lambda x: x[1].get("name", x[0])):
        title = f"{info.get('name', mid)} — `{mid}`"
        with st.expander(title, expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.json(info)
            with c2:
                if st.button("إلغاء الربط", key=f"acc_unlink_{mid}", type="secondary"):
                    ok, msg = auth.unlink_model(user, mid)
                    if ok:
                        st.toast(msg)
                        st.rerun()
                    else:
                        st.error(msg)
