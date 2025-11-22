import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import os

# ==========================================================
# Database Operations for Admin
# ==========================================================
class AdminDatabase:
    def __init__(self, db_path="database/users.db"):
        self.db_path = db_path
        self.kb_path = "data/knowledge_base.json"
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def load_knowledge_base(self):
        """Load knowledge base from JSON file"""
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_knowledge_base(self, knowledge_base):
        """Save knowledge base to JSON file"""
        os.makedirs("data", exist_ok=True)
        with open(self.kb_path, "w", encoding="utf-8") as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
    
    def get_usage_statistics(self):
        """Get comprehensive usage statistics"""
        conn = self.get_connection()
        
        daily_queries = pd.read_sql_query("""
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM messages 
            WHERE sender = 'user'
            GROUP BY DATE(timestamp) 
            ORDER BY date
        """, conn)
        
        top_topics = pd.read_sql_query("""
            SELECT m.message_content as query, COUNT(*) as frequency
            FROM messages m
            WHERE m.sender = 'user'
            GROUP BY m.message_content
            ORDER BY frequency DESC
            LIMIT 10
        """, conn)
        
        demographics = pd.read_sql_query("""
            SELECT age_group, language, COUNT(*) as count
            FROM users
            GROUP BY age_group, language
        """, conn)
        
        feedback_stats = pd.read_sql_query("""
            SELECT rating, COUNT(*) as count,
                   COUNT(CASE WHEN comment != '' THEN 1 END) as with_comments
            FROM feedback
            GROUP BY rating
        """, conn)
        
        conn.close()
        
        return {
            'daily_queries': daily_queries,
            'top_topics': top_topics,
            'demographics': demographics,
            'feedback_stats': feedback_stats
        }

# ==========================================================
# Enhanced Admin Dashboard
# ==========================================================
class EnhancedAdminDashboard:
    def __init__(self):
        self.db = AdminDatabase()
    
    def show_dashboard_overview(self):
        st.header("📊 Dashboard Overview")
        
        stats = self.db.get_usage_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_users = len(stats['demographics'])
        total_queries = stats['daily_queries']['count'].sum() if not stats['daily_queries'].empty else 0
        total_feedback = stats['feedback_stats']['count'].sum() if not stats['feedback_stats'].empty else 0
        positive_feedback = stats['feedback_stats'][
            stats['feedback_stats']['rating'] == 'up'
        ]['count'].sum() if not stats['feedback_stats'].empty else 0
        
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Total Queries", total_queries)
        with col3:
            st.metric("Health Topics", len(self.db.load_knowledge_base()))
        with col4:
            st.metric("Positive Feedback", f"{positive_feedback}/{total_feedback}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not stats['daily_queries'].empty:
                fig = px.line(
                    stats['daily_queries'], 
                    x='date', 
                    y='count',
                    title="📈 Daily Query Trends"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No query data available for trends")
        
        with col2:
            if not stats['feedback_stats'].empty:
                fig = px.pie(
                    stats['feedback_stats'],
                    values='count',
                    names='rating',
                    title="⭐ Feedback Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No feedback data available")
        
        st.subheader("🔝 Top Health Topics Queried")
        if not stats['top_topics'].empty:
            fig = px.bar(
                stats['top_topics'].head(5),
                x='frequency',
                y='query',
                orientation='h',
                title="Top 5 Queried Topics"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No query data available for top topics.")
    
    def manage_knowledge_base(self):
        st.header("📚 Knowledge Base Management")
        
        knowledge_base = self.db.load_knowledge_base()
        
        with st.expander("➕ Add New Health Topic"):
            with st.form("add_topic_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_topic = st.text_input("Topic Name", key="new_topic_name")
                    keywords = st.text_area("Keywords (comma-separated)")
                
                with col2:
                    description = st.text_area("Description")
                    remedy = st.text_area("Remedy/Advice")
                
                prevention = st.text_area("Prevention Tips")
                source = st.text_input("Source URL")
                
                if st.form_submit_button("💾 Save New Topic"):
                    if new_topic:
                        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
                        
                        knowledge_base[new_topic.lower()] = {
                            "keywords": keyword_list,
                            "description": description,
                            "remedy": remedy,
                            "prevention": prevention,
                            "source": source
                        }
                        
                        self.db.save_knowledge_base(knowledge_base)
                        st.success(f"✅ Added '{new_topic}' to knowledge base!")
                        st.rerun()
                    else:
                        st.error("❌ Topic name is required")
        
        st.subheader("📋 Existing Health Topics")
        
        if knowledge_base:
            topics = list(knowledge_base.keys())
            selected_topic = st.selectbox("Select topic to view or edit:", topics)
            
            if selected_topic:
                topic_data = knowledge_base[selected_topic]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Keywords:** {', '.join(topic_data.get('keywords', []))}")
                    st.write(f"**Description:** {topic_data.get('description', '')}")
                    st.write(f"**Remedy:** {topic_data.get('remedy', '')}")
                    st.write(f"**Prevention:** {topic_data.get('prevention', '')}")
                    st.write(f"**Source:** {topic_data.get('source', '')}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{selected_topic}"):
                        st.session_state.edit_topic = selected_topic
                    
                    if st.button("🗑️ Delete", key=f"delete_{selected_topic}"):
                        del knowledge_base[selected_topic]
                        self.db.save_knowledge_base(knowledge_base)
                        st.success(f"✅ Deleted '{selected_topic}'")
                        st.rerun()
                
                if st.session_state.get('edit_topic') == selected_topic:
                    with st.form(f"edit_form_{selected_topic}"):
                        st.subheader(f"✏️ Editing: {selected_topic}")
                        
                        new_keywords = st.text_area("Keywords",
                            value=', '.join(topic_data.get('keywords', [])))
                        new_description = st.text_area("Description",
                            value=topic_data.get('description', ''))
                        new_remedy = st.text_area("Remedy",
                            value=topic_data.get('remedy', ''))
                        new_prevention = st.text_area("Prevention",
                            value=topic_data.get('prevention', ''))
                        new_source = st.text_input("Source",
                            value=topic_data.get('source', ''))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes"):
                                knowledge_base[selected_topic] = {
                                    "keywords": [k.strip() for k in new_keywords.split(',') if k.strip()],
                                    "description": new_description,
                                    "remedy": new_remedy,
                                    "prevention": new_prevention,
                                    "source": new_source
                                }
                                self.db.save_knowledge_base(knowledge_base)
                                st.session_state.edit_topic = None
                                st.success("✅ Topic updated successfully!")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state.edit_topic = None
                                st.rerun()
        else:
            st.info("ℹ️ No health topics found in the knowledge base. Add your first topic above!")
    
    def user_management(self):
        st.header("👥 User Management")
        
        conn = self.db.get_connection()
        
        # Get users data
        users_query = """
            SELECT id, email, name, language, age_group, created_at
            FROM users 
            ORDER BY created_at DESC
        """
        users_df = pd.read_sql_query(users_query, conn)
        
        conn.close()
        
        if not users_df.empty:
            # Display users table
            st.subheader("📊 Registered Users")
            st.dataframe(users_df, use_container_width=True)
            
            # Display charts
            col1, col2 = st.columns(2)
            
            with col1:
                if not users_df.empty and 'age_group' in users_df.columns:
                    age_chart = users_df['age_group'].value_counts()
                    if not age_chart.empty:
                        fig = px.pie(
                            values=age_chart.values, 
                            names=age_chart.index,
                            title="👥 Age Group Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No age group data available")
            
            with col2:
                if not users_df.empty and 'language' in users_df.columns:
                    lang_chart = users_df['language'].value_counts()
                    if not lang_chart.empty:
                        fig = px.bar(
                            x=lang_chart.values, 
                            y=lang_chart.index,
                            orientation='h',
                            title="🌐 Language Preferences",
                            labels={'x': 'Number of Users', 'y': 'Language'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No language data available")
            
            # User statistics
            st.subheader("📈 User Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Users", len(users_df))
            with col2:
                most_common_lang = users_df['language'].mode()[0] if not users_df['language'].mode().empty else "N/A"
                st.metric("Most Common Language", most_common_lang)
            with col3:
                most_common_age = users_df['age_group'].mode()[0] if not users_df['age_group'].mode().empty else "N/A"
                st.metric("Most Common Age Group", most_common_age)
                
        else:
            st.info("ℹ️ No users found in the database.")
    
    def feedback_analysis(self):
        st.header("⭐ Feedback Analysis")
        
        conn = self.db.get_connection()
        
        # Get feedback data
        feedback_query = """
            SELECT f.rating, f.comment, f.timestamp, u.email, f.query, f.bot_response
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.timestamp DESC
        """
        feedback_df = pd.read_sql_query(feedback_query, conn)
        
        conn.close()
        
        if not feedback_df.empty:
            # Metrics
            col1, col2, col3 = st.columns(3)
            
            total_feedback = len(feedback_df)
            positive = len(feedback_df[feedback_df['rating'] == 'up'])
            negative = len(feedback_df[feedback_df['rating'] == 'down'])
            with_comments = len(feedback_df[feedback_df['comment'].notna() & (feedback_df['comment'] != '')])
            
            with col1:
                st.metric("Total Feedback", total_feedback)
            with col2:
                st.metric("Positive 👍", positive)
            with col3:
                st.metric("With Comments", with_comments)
            
            # Negative feedback with comments
            st.subheader("📌 Negative Feedback With Comments")
            
            negative_with_comments = feedback_df[
                (feedback_df["rating"] == "down") & 
                (feedback_df["comment"].notna()) & 
                (feedback_df["comment"].str.strip() != "")
            ]
            
            if not negative_with_comments.empty:
                # Display simplified table
                display_df = negative_with_comments[['rating', 'comment', 'timestamp']].copy()
                display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                st.dataframe(display_df, use_container_width=True)
                
                # Detailed expanders
                st.subheader("📋 Detailed Negative Feedback")
                for idx, row in negative_with_comments.iterrows():
                    with st.expander(f"❗ {row['email']} - {row['timestamp']}"):
                        st.write(f"**User Query:** {row['query']}")
                        st.write(f"**Bot Response:** {row['bot_response']}")
                        st.write(f"**User Comment:** {row['comment']}")
            else:
                st.success("🎉 No negative feedback with comments! Great job!")
            
            # Feedback distribution chart
            st.subheader("📊 Feedback Distribution")
            if not feedback_df.empty:
                rating_counts = feedback_df['rating'].value_counts()
                fig = px.pie(
                    values=rating_counts.values,
                    names=rating_counts.index,
                    title="Feedback Rating Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
                
        else:
            st.info("ℹ️ No feedback available in the database.")

    def run(self):
        # Create sidebar FIRST - this is critical
        with st.sidebar:
            st.title("🛠️ Admin Panel")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True, key="admin_logout"):
                st.session_state.admin_authenticated = False
                st.rerun()
            
            st.markdown("---")
            
            # Navigation
            page = st.radio(
                "Navigation",
                ["📊 Dashboard", "📚 Knowledge Base", "👥 User Management", "⭐ Feedback Analysis"],
                key="admin_navigation"
            )
        
        # Main content area
        if page == "📊 Dashboard":
            self.show_dashboard_overview()
        elif page == "📚 Knowledge Base":
            self.manage_knowledge_base()
        elif page == "👥 User Management":
            self.user_management()
        elif page == "⭐ Feedback Analysis":
            self.feedback_analysis()