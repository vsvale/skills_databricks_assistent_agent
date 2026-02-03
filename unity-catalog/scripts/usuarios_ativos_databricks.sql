SELECT
      date_format(event_time, 'yyyy-MM') AS year_month,
      COUNT(DISTINCT COALESCE(user_identity.email, request_params.user)) AS active_users
    FROM
      system.access.audit
    WHERE
      action_name IS NOT NULL
      AND COALESCE(user_identity.email, request_params.user) IS NOT NULL
      AND (
        user_agent LIKE '%Mozilla%'
        OR user_agent LIKE '%Chrome%'
        OR user_agent LIKE '%Safari%'
        OR user_agent LIKE '%AppleWebKit%'
        OR user_agent LIKE '%Edge%'
      )
      AND workspace_id = dataops_prd.libs.get_workspace_id()
    GROUP BY
      year_month