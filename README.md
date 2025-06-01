### 코드 작동 flow

![Image](https://github.com/user-attachments/assets/af5d63a0-98ea-41c6-aa19-8ad344b2a8e5)
1. `streamlit run streamlit_demo.py`로 streamlit 실행
2. 이미지 업로드 시 analysis agent가 input_image MCP 서버를 사용해 메뉴 이미지 분석 및 필요한 식료품 반환
3. query agent가 MongoDB MCP 서버를 활용해 식료품 데이터를 DB에서 쿼리

&nbsp;
&nbsp;

### 데모 이미지

<img width="938" alt="Image" src="https://github.com/user-attachments/assets/3ba31286-4702-4a80-8ef4-2e30de8fc3b8" />
