async function client(
    endpoint,
    { data, headers: customHeaders, ...customConfig } = {}
  ) {
    const config = {
      method: data ? "POST" : "GET",
      body: data ? JSON.stringify(data) : undefined,
      headers: {
        ...customHeaders,
      },
      ...customConfig,
    };
  
    if (data) {
      config.headers = { ...config.headers, "Content-Type": "application/json" };
    }
  
    return window.fetch(endpoint, config).then(async (response) => {  
      if (response.ok) {
        if (response.status === 204 || response.status === 200 ) {
          return;
        }
        const jsonResponse = await response.json();
        return jsonResponse;
      } else {
        const jsonResponse = await response.json();
        await Promise.reject(JSON.stringify(jsonResponse));
      }
    });
  }
  
  export { client };
  