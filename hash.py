import streamlit_authenticator as stauth

# Try the static method approach
hashed_password = stauth.Hasher.hash('123')
print(hashed_password)