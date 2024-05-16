// @ts-check

/**
 * Fetches data from an endpoint X times and tracks response times.
 *
 * @param {() => Promise<Response>} fetchCallback - The function to be called to fetch data.
 * @param {number} x - The number of times the fetch operation should be performed.
 * @returns {Promise<{averageResponseTime: number, errors: number}>} - The average response time and number of errors.
 */
async function fetchFromEndpointXTimes(fetchCallback, x = 10) {
  let totalDuration = 0;
  let errors = 0;

  console.info() // blank line after prompt for better readability

  for (let i = 0; i < x; i++) {
    try {
      const startTime = Date.now();
      const response = await fetchCallback();
      const endTime = Date.now();

      const duration = endTime - startTime;
      totalDuration += duration;

      console.info('Status:', response?.status, '/', 'Duration:', duration, 'ms', '/', 'Total queries:', i + 1, );
      // console.info('Attempt', i + 1, 'Status:', response?.status, '/', 'Duration:', duration, 'ms', '/');
    } catch (err) {
      console.error('Error: ', err);
      errors++;
    }
  }

  return {
    averageResponseTime: totalDuration / x,
    errors,
  };
}

// TODO: click "Copy as fetch (Node.js)" in the browser Network tab + paste here */
const fetchCallback = () => fetch('...')

const x = 50

fetchFromEndpointXTimes(fetchCallback, x)
  .then(results => {
    console.log('\nAverage response time:', results.averageResponseTime, 'ms');
    console.log('Error rate:', results.errors / x, '%');
  })
  .catch(error => {
    console.error('An error occurred:', error);
  });