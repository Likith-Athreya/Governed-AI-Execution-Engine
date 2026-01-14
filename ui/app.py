import streamlit as st, requests, pandas as pd

API_BASE = "http://127.0.0.1:8000"
st.set_page_config(page_title="Governed AI Execution Engine", layout="wide")

page = st.sidebar.selectbox("Navigation", ["Main", "Audit Logs", "Policy Playground"])

def safe_json(res):
    try: return res.json()
    except: return {"error": res.text}

def display_result(data):
    if not data: return
    if data.get("operation") == "UPDATE":
        st.success("✅ UPDATE successful!")
        st.metric("Rows Affected", data.get("rows_affected", 0))
    elif "columns" in data and data["rows"]:
        st.dataframe(pd.DataFrame(data["rows"], columns=data["columns"]))
    else:
        st.info("No results")

st.title("Governed AI Execution Engine")
st.caption("Natural language → simulation → governed execution")

if page == "Main":
    st.subheader("1. Natural Language Query")

    user_input = st.text_area(
        "Ask a data question",
        placeholder="give customer name",
        height=80
    )

    human_free = st.toggle("Human-Free Execution", value=False, key="human_free_main")
    st.caption("When enabled, the system uses episodic memory for autonomous decision-making")

    st.session_state["human_free"] = human_free

    simulate_btn = st.button("Simulate")

    if simulate_btn and user_input:
        human_free = st.session_state.get("human_free", False)

        with st.spinner("Interpreting and simulating..."):
            res = requests.post(
                f"{API_BASE}/nl_simulate",
                json={
                    "user_input": user_input,
                    "human_free": human_free
                }
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
            query_type = simulation.get("query_type", "SELECT")
            if query_type == "UPDATE":
                st.json({
                    "Query Type": query_type,
                    "Tables": simulation.get("tables_accessed"),
                    "Rows Affected": simulation.get("rows_affected", 0),
                    "Execution Time (ms)": simulation.get("execution_time_ms")
                })
            else:
                st.json({
                    "Query Type": query_type,
                    "Tables": simulation.get("tables_accessed"),
                    "Rows Returned": simulation.get("rows_returned", 0),
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

            if human_free:
                st.info("🤖 Human-free mode enabled. Proceeding with autonomous execution...")

                with st.spinner("Executing governed query autonomously..."):
                    res = requests.post(
                        f"{API_BASE}/execute",
                        json={
                            "sql": plan["sql"],
                            "simulation": simulation,
                            "user_input": user_input,
                            "human_free": True
                        }
                    )

                    if res.status_code == 200:
                        result = safe_json(res)
                        st.success("🎉 Autonomous execution completed successfully!")

                        st.markdown("### Executed SQL")
                        st.code(result["sql"], language="sql")

                        st.markdown("### Simulation Summary")
                        st.json(result["simulation"])

                        st.markdown("### Query Result")
                        display_result(result.get("data"))

                        st.markdown("### 🧠 Episodic Memory Update")
                        st.info("This query has been stored in episodic memory for future autonomous decision-making.")
                    else:
                        st.error("❌ Autonomous execution denied")
                        st.json(safe_json(res))

                st.stop()

    if "plan" in st.session_state and "simulation" in st.session_state:
        plan = st.session_state["plan"]
        simulation = st.session_state["simulation"]

        human_free = st.session_state.get("human_free", False)
        if not human_free:
            st.subheader("4. Execution")

            query_type = simulation.get("query_type", "SELECT")
            can_execute = (
                simulation.get("valid")
                and query_type in ["SELECT", "UPDATE"]
                and "PII" not in simulation.get("column_classification", {}).values()
            )

            if can_execute:
                if st.button("Execute Query"):
                    execution_placeholder = st.empty()
                    execution_placeholder.info("🔄 Requesting execution approval and processing...")

                    with st.spinner("Executing governed query..."):
                        res = requests.post(
                            f"{API_BASE}/execute",
                            json={
                                "sql": plan["sql"],
                                "simulation": simulation,
                                "user_input": st.session_state.get("user_input", ""),
                                "human_free": human_free
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
                        display_result(result.get("data"))

                    else:
                        st.error("Execution denied")
                        st.json(safe_json(res))
        else:
            st.info("Execution disabled due to simulation result.")

if page == "Audit Logs":
    st.subheader("Audit Logs")

    if st.button("🔄 Refresh") or "audit_logs" not in st.session_state:
        try:
            logs = safe_json(requests.get(f"{API_BASE}/audit_logs", timeout=5))
            st.session_state["audit_logs"] = logs.get("logs", logs) if isinstance(logs, dict) else logs
        except:
            st.session_state["audit_logs"] = []
            st.error("Failed to load audit logs")

    logs_list = st.session_state.get("audit_logs", [])
    if not logs_list:
        st.info("No audit logs found")
    else:
        st.caption(f"Showing {len(logs_list)} logs")
        for log in logs_list:
            with st.expander(f"{log.get('timestamp', 'Unknown')} - {log.get('decision', 'UNKNOWN')}"):
                st.write(f"**Input:** {log.get('user_input', 'N/A')}")
                st.code(log.get("sql", ""), language="sql")
                st.write(f"**Reason:** {log.get('reason', 'N/A')}")
                st.json(log.get("simulation", {}))

if page == "Policy Playground":
    st.subheader("Policy Playground")

    policy_text = st.text_area("Describe policy", "Block PII, limit to 10 rows", height=80)

    if st.button("Test Policy"):
        with st.spinner("Testing policy..."):
            try:
                policy_res = safe_json(requests.post(f"{API_BASE}/policy/interpreter", json={"policy_text": policy_text}))
                if policy_res.get("status") == "ok":
                    st.session_state["test_policy"] = policy_res["policy"]
                    what_if_res = safe_json(requests.post(f"{API_BASE}/policy/what_if", json={
                        "policy": policy_res["policy"],
                        "sql": "SELECT v.vendor_name FROM vendors v LIMIT 1"
                    }))
                    st.success("Policy tested successfully")
                    st.json(policy_res["policy"])
                    if what_if_res.get("llm_explanation"):
                        st.write(what_if_res["llm_explanation"])
                else:
                    st.error("Policy interpretation failed")
            except:
                st.error("Policy test failed")

    if st.button("Activate Policy") and "test_policy" in st.session_state:
        with st.spinner("Activating..."):
            try:
                res = safe_json(requests.post(f"{API_BASE}/policy/activate", json=st.session_state["test_policy"]))
                if res.get("status") == "activated":
                    st.success("Policy activated!")
                    st.json(res["policy"])
                else:
                    st.error("Activation failed")
            except:
                st.error("Activation failed")