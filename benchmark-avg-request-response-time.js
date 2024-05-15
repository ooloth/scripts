// @ts-check

/**
 * Fetches data from an endpoint X times and tracks response times.
 *
 * @param {() => Promise<Response>} fetchCallback - The function to be called to fetch data.
 * @param {number} x - The number of times the fetch operation should be performed.
 * @returns {Promise<{averageResponseTime: number, errors: number}>} - The average response time and number of errors.
 */
async function fetchFromEndpointXTimes(fetchCallback, x) {
  let totalResponseTime = 0;
  let errors = 0;

  console.info() // blank line after prompt for better readability

  for (let i = 0; i < x; i++) {
    try {
      const startTime = Date.now();
      const response = await fetchCallback();
      const endTime = Date.now();

      const responseTime = endTime - startTime;
      totalResponseTime += responseTime;

      console.info('Status:', response?.status, '/', 'Duration:', responseTime, 'ms', '/', 'Total queries:', i + 1, );
    } catch (err) {
      console.error('Error: ', err);
      errors++;
    }
  }

  return {
    averageResponseTime: totalResponseTime / x,
    errors,
  };
}

// Everything after "=>" came from "Copy as fetch (Node.js)" in the browser Network tab
const internalMapAppPerturbationsEndpointSearchForLetterS = () => fetch("https://catalyst.rxrx.io/phenoapp/api/v0/perturbations?concentration_compound_range=0,10&concentration_sf_range=1e-9,0.1&filter_tags=&gene_expression_threshold=-3&group_label=HUVEC-tvn_v16_prox_bias_reduced-DL2-2024-05-13&ignore_gene_threshold=false&include_control_wells=false&pairwise=false&perturbations=&pvalue=0.01&search=s&split_by=", {
  "headers": {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "test=test; auth0_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik1pY2hhZWwgVWxvdGgiLCJlbWFpbCI6Ik1pY2hhZWwuVWxvdGhAcmVjdXJzaW9ucGhhcm1hLmNvbSIsImV4cCI6MTcxNTg3NzY0Nn0.CGszYDRorzVzIeFWH7umbhN09ZUkEP2a1KIhVSO5dso; profile=eyJzdWIiOiJzYW1scHxPa3RhLVJlY3Vyc2lvbi1TQU1MfG1pY2hhZWwudWxvdGhAcmVjdXJzaW9ucGhhcm1hLmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIiwiZmFtaWx5X25hbWUiOiJVbG90aCIsIm5pY2tuYW1lIjoibWljaGFlbC51bG90aCIsIm5hbWUiOiJNaWNoYWVsIFVsb3RoIiwicGljdHVyZSI6Imh0dHBzOi8vcy5ncmF2YXRhci5jb20vYXZhdGFyL2I4Y2Q0YmQyN2Q4YTU2YTIxMjQ4NjQ3YjNjZGY0ZmU5P3M9NDgwJnI9cGcmZD1odHRwcyUzQSUyRiUyRmNkbi5hdXRoMC5jb20lMkZhdmF0YXJzJTJGbXUucG5nIiwidXBkYXRlZF9hdCI6IjIwMjQtMDUtMTVUMTY6NDA6NDQuMjA5WiIsImVtYWlsIjoiTWljaGFlbC5VbG90aEByZWN1cnNpb25waGFybWEuY29tIiwiaHR0cHM6Ly9vcGEucnhyeC5pby9jbGFpbXMvZ3JvdXBzIjpbIlZQTi1Vc2VycyIsIlZhbGVuY2UgRGlzY292ZXJ5IENhbGVuZGFyIFZpZXciLCJhcHBfcGFnZXJkdXR5X3VzZXIiLCJPU0IgQW5jaG9yIiwiT1NIIC0gVGVjaCBQbGF0Zm9ybXMiLCJHb29nbGVBY3RpdmVVc2VycyIsIlJQLTAwNi1OZXVyby1EYXRhTGFrZSIsIkdvb2dsZVVzZXJzIiwiRW1wbG95ZWVzIiwiYXBwX0ZpZ21hIiwiQWxsIEVtcGxveWVlcyIsInN0cmVhbS1hbGlnbmVkLXRlYW1zIiwiYWxsXmVtcGxveWVlcyIsIlE0X1Bhc3N3b3JkX0NvbXBsaWFuY2UiLCJSZWN1cnNpb24gUGhhcm1hY2V1dGljYWxzIiwiZ2tlLXNlY3VyaXR5LWdyb3VwcyIsImFwcF9yZ19yeHJ4X2FkbWluIiwiRW5naW5lZXJpbmciLCJzYXQtYmlvbG9neSIsIkRvY2tlciIsIlBBTV9TU19Vc2VycyIsImFwcF92ZXJrYWRhX2dlbmVyYWwiLCJBcGVzIFRlYW0iLCJTTl9TY2llbnRpZmljX0VuZ2luZWVyaW5nIiwiRXZlcnlvbmUiLCJhcHBfZGFzaCIsImluZC13b3JrZmxvd3MtYWRtaW5zIiwiYXBwX21vbmRheSIsIlRlY2ggT3JnIiwiUmVjdXJzaW9uIENhbmFkYSIsImRhdGEtbmF2aWdhdGlvbiIsInJwMDA2LXByb2Qtc3JlIiwiRGF0YUxha2VfYXBwX3BoZW5vYXBwX2ludGVybmFsIiwiZG9tYWluXnVzZXJzIiwiT1NCIEluZHVzdHJpYWxpemVkIFZpc3VhbGl6YXRpb24iLCJFbmRVc2VyX1Bhc3N3b3JkX1BvbGljeSIsInBoZW5vbWFwLWRldi11c2VycyIsIkRvbWFpbiBVc2VycyIsImFwcF9waGVub2FwcF9hZG1pbiIsIlBoZW5vbWFwLURhdGFsYWtlIiwiZXhwZXJpbWVudC1leGVjdXRpb24tYWRtaW5zIiwiYXBwX2FzYW5hX21lbWJlcl9hY2Nlc3MiLCJBY3RpdmUgRW1wbG95ZWVzIiwiYXBwX3BoZW5vYXBwX2ludGVybmFsIiwibngtZG93bmxvYWQiXX0=",
    "Referer": "https://catalyst.rxrx.io/phenoapp/?cosim=-0.6,0.6&groupLabel=HUVEC-tvn_v16_prox_bias_reduced-DL2-2024-05-13&pertTypes=compound,gene&pvalue=0.01",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "body": null,
  "method": "GET"
});

fetchFromEndpointXTimes(internalMapAppPerturbationsEndpointSearchForLetterS, 50)
  .then(results => {
    console.log('\nAverage response time:', results.averageResponseTime, 'ms');
    console.log('Number of errors:', results.errors);
  })
  .catch(error => {
    console.error('An error occurred:', error);
  });