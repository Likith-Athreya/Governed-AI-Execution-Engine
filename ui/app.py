import streamlit as st
import requests
import pandas as pd

API_BASE = "http://127.0.0.1:8000"

def safe_json(res):
    try:
        return res.json()
    except Exception:
        return {"error": res.text}


st.set_page_config(
    page_title="Governed AI Execution Engine",
    layout="wide"
)

st.title("Governed AI Execution Engine")
st.caption("Natural language → simulation → governed execution")

st.subheader("1. Natural Language Query")

user_input = st.text_area(
    "Ask a data question",
    placeholder="give customer name",
    height=80
)

simulate_btn = st.button("Simulate")

if simulate_btn and user_input:
    with st.spinner("Interpreting and simulating..."):
        res = requests.post(
            f"{API_BASE}/nl_simulate",
            json={"user_input": user_input}
        )

        if res.status_code != 200:
            st.error("Simulation failed")
            st.text(res.text)
            st.stop()

        data = res.json()

    if data.get("status") != "ok":
        st.error("LLM failed to generate a valid plan")
        st.json(data)
        st.stop()

    plan = data["plan"]
    simulation = data["simulation"]

    st.session_state["plan"] = plan
    st.session_state["simulation"] = simulation
    st.session_state["user_input"] = user_input

    st.subheader("2. LLM Action Plan")
    st.json(plan)

    st.markdown("**Generated SQL**")
    st.code(plan["sql"], language="sql")

    st.subheader("3. Simulation Result")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Query Impact")
        st.json({
            "Query Type": simulation.get("query_type"),
            "Tables": simulation.get("tables_accessed"),
            "Rows Returned": simulation.get("rows_returned"),
            "Execution Time (ms)": simulation.get("execution_time_ms")
        })

    with col2:
        st.markdown("### Column Classification")
        st.json(simulation.get("column_classification"))

    pii_detected = "PII" in simulation.get("column_classification", {}).values()
    valid = simulation.get("valid", False)

    if not valid:
        st.error("Simulation failed. Query is invalid.")
    elif pii_detected:
        st.warning("PII detected. Execution will be blocked.")
    else:
        st.success("Simulation passed. Query eligible for execution.")

if "plan" in st.session_state and "simulation" in st.session_state:
    plan = st.session_state["plan"]
    simulation = st.session_state["simulation"]

    st.subheader("4. Execution")

    can_execute = (
        simulation.get("valid")
        and simulation.get("query_type") == "SELECT"
        and "PII" not in simulation.get("column_classification", {}).values()
    )

    if can_execute:
        if st.button("Execute Query"):
            with st.spinner("Executing governed query..."):
                res = requests.post(
                    f"{API_BASE}/execute",
                    json={
                        "sql": plan["sql"],
                        "simulation": simulation,
                        "user_input": st.session_state.get("user_input", "")
                    }
                )

                if res.status_code == 200:
                    result = safe_json(res)
                    st.success("Query executed successfully")

                    st.markdown("### Executed SQL")
                    st.code(result["sql"], language="sql")

                    st.markdown("### Simulation Summary")
                    st.json(result["simulation"])

                    st.markdown("### Query Result")
                    data = result.get("data")

                    if data and "columns" in data and "rows" in data:
                        df = pd.DataFrame(data["rows"], columns=data["columns"])
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"Rows returned: {len(df)}")
                    else:
                        st.info("No data returned")

                else:
                    st.error("Execution denied")
                    st.json(safe_json(res))
    else:
        st.info("Execution disabled due to simulation result.")

st.divider()
st.subheader("AUDIT LOG VIEWER")

# Auto-load logs on page load if not already loaded
if "audit_logs" not in st.session_state:
    try:
        res = requests.get(f"{API_BASE}/audit_logs", timeout=5)
        if res.status_code == 200:
            logs = res.json()
            logs_list = logs.get("logs", []) if isinstance(logs, dict) else logs
            st.session_state["audit_logs"] = logs_list
        else:
            st.session_state["audit_logs"] = []
            st.session_state["audit_logs_error"] = f"Failed to load audit logs: {res.status_code} - {res.text}"
    except requests.exceptions.RequestException as e:
        st.session_state["audit_logs"] = []
        st.session_state["audit_logs_error"] = f"Connection error: {str(e)}"
    except Exception as e:
        st.session_state["audit_logs"] = []
        st.session_state["audit_logs_error"] = f"Error loading audit logs: {str(e)}"

# Refresh button
col1, col2 = st.columns([1, 10])
with col1:
    if st.button("🔄 Refresh"):
        try:
            res = requests.get(f"{API_BASE}/audit_logs", timeout=5)
            if res.status_code == 200:
                logs = res.json()
                logs_list = logs.get("logs", []) if isinstance(logs, dict) else logs
                st.session_state["audit_logs"] = logs_list
                st.session_state["audit_logs_error"] = None
                st.success("Audit logs refreshed")
            else:
                st.session_state["audit_logs"] = []
                st.session_state["audit_logs_error"] = f"Failed to load audit logs: {res.status_code} - {res.text}"
        except requests.exceptions.RequestException as e:
            st.session_state["audit_logs"] = []
            st.session_state["audit_logs_error"] = f"Connection error: {str(e)}"
        except Exception as e:
            st.session_state["audit_logs"] = []
            st.session_state["audit_logs_error"] = f"Error loading audit logs: {str(e)}"

# Display logs
logs_list = st.session_state.get("audit_logs", [])
error = st.session_state.get("audit_logs_error")

if error:
    st.error(error)
    st.info("Make sure the API server is running at http://127.0.0.1:8000")

if not logs_list:
    st.info("No audit logs found")
else:
    st.caption(f"Showing {len(logs_list)} audit log(s)")
    for log in logs_list:
        decision = log.get("decision", "UNKNOWN")
        timestamp = log.get("timestamp", "Unknown time")
        with st.expander(f"{timestamp} - {decision}"):
            st.markdown("**User Input**")
            st.write(log.get("user_input", "N/A"))

            st.markdown("**SQL**")
            st.code(log.get("sql", ""), language="sql")

            st.markdown("**Decision Reason**")
            st.write(log.get("reason", "N/A"))

            st.markdown("**Simulation Evidence**")
            st.json(log.get("simulation", {}))




    

