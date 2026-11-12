"""SQL-backed Streamlit dashboard for LearnSphere operations investigations."""

import os

import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="LearnSphere Operations", page_icon="📚", layout="wide")
st.title("LearnSphere | Operations & Technical Support")
st.caption("Investigate payments, subscriptions, class attendance, and support SLAs with MySQL.")


@st.cache_resource
def get_connection():
    required = ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(f"Missing database environment variables: {', '.join(missing)}")
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.getenv("MYSQL_DATABASE", "learnsphere"),
        charset="utf8mb4",
    )


def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql(sql, get_connection(), params=params)


try:
    kpis = query(
        """
        SELECT
            (SELECT COUNT(*) FROM Students) AS students,
            (SELECT COUNT(*) FROM Teachers WHERE status = 'Active') AS active_teachers,
            (SELECT COUNT(*) FROM Payments WHERE payment_status = 'Successful') AS successful_payments,
            (SELECT COALESCE(SUM(amount), 0) FROM Payments WHERE payment_status = 'Successful') AS successful_revenue,
            (SELECT COUNT(*) FROM Support_Tickets WHERE status <> 'Resolved'
                AND priority IN ('High', 'Critical')) AS urgent_open_tickets
        """
    ).iloc[0]
    country_data = query(
        """
        SELECT COALESCE(country, 'Not provided') AS country, COUNT(*) AS students
        FROM Students GROUP BY country ORDER BY students DESC
        """
    )
    payment_data = query(
        """
        SELECT payment_status, COUNT(*) AS payment_count, SUM(amount) AS amount_total
        FROM Payments GROUP BY payment_status ORDER BY payment_count DESC
        """
    )
    ticket_data = query(
        """
        SELECT priority, status, COUNT(*) AS ticket_count
        FROM Support_Tickets GROUP BY priority, status
        ORDER BY FIELD(priority, 'Critical', 'High', 'Medium', 'Low')
        """
    )
    teacher_data = query(
        """
        SELECT t.name AS teacher, t.subject, COUNT(c.class_id) AS classes,
               ROUND(100 * AVG(c.status = 'Cancelled'), 1) AS cancellation_rate_pct
        FROM Teachers AS t
        JOIN Classes AS c ON c.teacher_id = t.teacher_id
        GROUP BY t.teacher_id, t.name, t.subject
        HAVING COUNT(c.class_id) >= 10
        ORDER BY cancellation_rate_pct DESC
        LIMIT 10
        """
    )
    payment_mismatch = query(
        """
        SELECT s.student_id, s.name, p.payment_id, p.amount, p.payment_date,
               sub.status AS subscription_status
        FROM Students AS s
        JOIN Payments AS p ON p.student_id = s.student_id
        WHERE p.payment_status = 'Successful'
          AND NOT EXISTS (
              SELECT 1 FROM Subscriptions AS sub
              WHERE sub.student_id = s.student_id AND sub.status = 'Active'
          )
        ORDER BY p.payment_date DESC
        LIMIT 50
        """
    )
except (mysql.connector.Error, RuntimeError, ValueError) as error:
    st.error(f"Could not load dashboard data: {error}")
    st.info("Apply sql/schema.sql, configure the database variables in .env, then load sample data.")
    st.stop()

metric_columns = st.columns(5)
metric_columns[0].metric("Students", f"{int(kpis['students']):,}")
metric_columns[1].metric("Active teachers", f"{int(kpis['active_teachers']):,}")
metric_columns[2].metric("Successful payments", f"{int(kpis['successful_payments']):,}")
metric_columns[3].metric("Successful revenue", f"${float(kpis['successful_revenue']):,.2f}")
metric_columns[4].metric("Urgent unresolved tickets", f"{int(kpis['urgent_open_tickets']):,}")

left, right = st.columns(2)
with left:
    st.subheader("Students by country")
    st.plotly_chart(
        px.bar(country_data, x="country", y="students", color="students"),
        use_container_width=True,
    )
with right:
    st.subheader("Payment outcomes")
    st.plotly_chart(
        px.pie(payment_data, names="payment_status", values="payment_count", hole=0.45),
        use_container_width=True,
    )

left, right = st.columns(2)
with left:
    st.subheader("Support tickets by priority and status")
    st.plotly_chart(
        px.bar(ticket_data, x="priority", y="ticket_count", color="status", barmode="stack"),
        use_container_width=True,
    )
with right:
    st.subheader("Teachers by cancellation rate")
    st.plotly_chart(
        px.bar(
            teacher_data,
            x="cancellation_rate_pct",
            y="teacher",
            color="subject",
            orientation="h",
            hover_data=["classes"],
        ),
        use_container_width=True,
    )

st.subheader("Successful payment without an active subscription")
st.caption("A result is an investigation lead, not proof of a billing or provisioning defect.")
st.dataframe(payment_mismatch, use_container_width=True, hide_index=True)
