import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="Grade Analysis Tool",
    page_icon="📊",
    layout="wide"
)

# 제목
st.title("🎓 성적 분석 도구")
st.markdown("---")

# 과목 리스트
subjects = ['국어', '영어', '수학', '과학', '사회']

# 세션 스테이트 초기화
if 'saved_weights' not in st.session_state:
    st.session_state.saved_weights = {}

# 사이드바 - 대학별 가중치 설정
st.sidebar.header("🏫 대학별 가중치 설정")

# 대학 이름 입력
university_name = st.sidebar.text_input("대학명을 입력하세요:", placeholder="예: 서울대")

# 가중치 설정
st.sidebar.subheader("과목별 가중치 (%)")
weights = {}
total_weight = 0

for subject in subjects:
    weight = st.sidebar.slider(f"{subject}", 0, 100, 20, key=f"weight_{subject}")
    weights[subject] = weight
    total_weight += weight

# 가중치 합계 확인
if total_weight != 100:
    st.sidebar.error(f"⚠️ 가중치 합계가 {total_weight}%입니다. 100%로 맞춰주세요!")
else:
    st.sidebar.success("✅ 가중치 합계 100%")

# 가중치 저장
if st.sidebar.button("가중치 저장") and university_name and total_weight == 100:
    st.session_state.saved_weights[university_name] = weights.copy()
    st.sidebar.success(f"✅ {university_name} 가중치가 저장되었습니다!")

# 저장된 가중치 불러오기
if st.session_state.saved_weights:
    st.sidebar.subheader("📋 저장된 대학")
    selected_university = st.sidebar.selectbox(
        "대학을 선택하세요:",
        ["선택안함"] + list(st.session_state.saved_weights.keys())
    )

    if selected_university != "선택안함":
        # 선택된 대학의 가중치로 업데이트
        saved_weights = st.session_state.saved_weights[selected_university]
        for subject in subjects:
            st.session_state[f"weight_{subject}"] = saved_weights[subject]
        st.rerun()

# 메인 화면 - 성적 입력
col1, col2 = st.columns(2)

with col1:
    st.header("📝 중간고사 성적 입력")
    mid_scores = {}
    for subject in subjects:
        mid_scores[subject] = st.number_input(
            f"{subject} (중간고사)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            key=f"mid_{subject}"
        )

with col2:
    st.header("📝 기말고사 성적 입력")
    final_scores = {}
    for subject in subjects:
        final_scores[subject] = st.number_input(
            f"{subject} (기말고사)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            key=f"final_{subject}"
        )

# 분석 버튼
if st.button("🔍 성적 분석하기", type="primary"):
    if all(score > 0 for score in mid_scores.values()) and all(score > 0 for score in final_scores.values()):

        # 데이터 준비
        analysis_data = []

        for univ_name, univ_weights in st.session_state.saved_weights.items():
            # 중간고사 가중 점수 계산
            mid_weighted = sum(mid_scores[subject] * univ_weights[subject] / 100 for subject in subjects)
            # 기말고사 가중 점수 계산
            final_weighted = sum(final_scores[subject] * univ_weights[subject] / 100 for subject in subjects)
            # 변화량 계산
            change = final_weighted - mid_weighted

            analysis_data.append({
                '대학': univ_name,
                '중간고사': round(mid_weighted, 2),
                '기말고사': round(final_weighted, 2),
                '변화량': round(change, 2)
            })

        if analysis_data:
            df = pd.DataFrame(analysis_data)

            # 결과 표시
            st.markdown("---")
            st.header("📊 분석 결과")

            # 데이터 테이블
            st.subheader("📋 대학별 점수 요약")
            st.dataframe(df, use_container_width=True)

            # 가장 유리한 대학 추천
            best_university = df.loc[df['기말고사'].idxmax()]
            st.success(f"🏆 **가장 유리한 대학**: {best_university['대학']} (기말고사 기준: {best_university['기말고사']}점)")

            # 시각화
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 대학별 성적 비교")
                fig_bar = px.bar(
                    df,
                    x='대학',
                    y=['중간고사', '기말고사'],
                    title="대학별 가중 점수 비교",
                    barmode='group'
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.subheader("🔄 성적 변화량")
                fig_change = px.bar(
                    df,
                    x='대학',
                    y='변화량',
                    title="대학별 성적 변화량",
                    color='변화량',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_change, use_container_width=True)

            # 과목별 성적 변화 분석
            st.subheader("📚 과목별 성적 변화")
            subject_changes = []
            for subject in subjects:
                change = final_scores[subject] - mid_scores[subject]
                subject_changes.append({
                    '과목': subject,
                    '중간고사': mid_scores[subject],
                    '기말고사': final_scores[subject],
                    '변화량': round(change, 2)
                })

            subject_df = pd.DataFrame(subject_changes)

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(subject_df, use_container_width=True)

            with col2:
                fig_subject = px.bar(
                    subject_df,
                    x='과목',
                    y='변화량',
                    title="과목별 점수 변화",
                    color='변화량',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_subject, use_container_width=True)

            # 레이더 차트
            if len(df) > 0:
                st.subheader("🎯 대학별 성적 레이더 차트")

                fig_radar = go.Figure()

                for _, row in df.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[row['중간고사'], row['기말고사']],
                        theta=['중간고사', '기말고사'],
                        fill='toself',
                        name=row['대학']
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="대학별 성적 비교 (레이더 차트)"
                )

                st.plotly_chart(fig_radar, use_container_width=True)

    else:
        st.error("⚠️ 모든 과목의 성적을 입력해주세요!")

# 사용법 안내
with st.expander("📖 사용법 안내"):
    st.markdown("""
### 사용 순서
1. **좌측 사이드바**에서 대학명 입력
2. **과목별 가중치** 설정 (합계 100%가 되도록)
3. **가중치 저장** 버튼 클릭
4. 여러 대학의 가중치를 저장하여 비교 가능
5. **중간고사/기말고사 성적** 입력
6. **성적 분석하기** 버튼 클릭

### 주요 기능
- 🏫 대학별 가중치 설정 및 저장
- 📊 대학별 가중 점수 계산
- 📈 성적 변화량 분석
- 🎯 다양한 시각화 (막대그래프, 레이더차트)
- 🏆 가장 유리한 대학 자동 추천
""")

# 푸터
st.markdown("---")
st.markdown("**팁**: 다양한 대학의 가중치를 미리 저장해두면 쉽게 비교할 수 있습니다!")