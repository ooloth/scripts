/**
 * Purpose: Test our scraping alerts that detect /heatmap queries made by the same user over various time periods.
 * @param {number} x
 * @param {number} y
 */
function fetchHeatmapEveryXSecForYSec(x, y) {
  let queryCount = 0

  const interval = setInterval(async () => {
    const response = await fetch("https://mapapp.rg.rxrx.app/api/v1/heatmap?concentration_compound_range=0,10&concentration_sf_range=1e-9,0.1&cosim=-0.6,0.6&filter_tags=&group_label=iPSC-NGN2-NEURON-2wk_postpoc_tvn-DL2_cpca_v2_v3_v4_v5_iter_1-2023-02-24&ignore_gene_threshold=false&include_control_wells=false&include_disabled_perturbations=false&known_relationships=false&llm_relationships=false&map_normalized_values=false&pairwise=false&perturbation_types=compound,gene&perturbations=ACTB&pvalue=0.01&split_by=", {
      "headers": {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "_pomerium=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiYXV0aGVudGljYXRlLmV4dGVybmFsLWFjY2Vzcy5yeHJ4LmFwcCIsIm1hcGFwcC5yZy5yeHJ4LmFwcCJdLCJkYXRhYnJva2VyX3JlY29yZF92ZXJzaW9uIjo5MjM0NDcsImRhdGFicm9rZXJfc2VydmVyX3ZlcnNpb24iOjE0OTEwNzAzMzA4ODM3MDA0MDk0LCJpYXQiOjE3MDEzNTcxNjEsImlkcF9pZCI6IjNjWjNIdTltYUQ5UTdCYk5tMnBHdHg4WEphR3U2QnN2SFVxUmRudDU4UkozIiwiaXNzIjoiYXV0aGVudGljYXRlLmV4dGVybmFsLWFjY2Vzcy5yeHJ4LmFwcCIsImp0aSI6IklELkNjUzhVd0V2eEFPaWZ6SnpNVkQ1d1J6blZiZk9rMjdtNWZ0Z3Zjcjd6TUUiLCJzdWIiOiIwMHVqMWticG5yd1pGMGJWcjM1NyJ9.6cthulck71CGP8yllTJu0PSDwqVJ-NXEuHzsXLYRqYU",
        "Referer": "https://mapapp.rg.rxrx.app/?53616c7465645f5fd35382b1159df31a2a60bef3df5dcba82dac9a3d8622936c709d7296c9e5416f5e156b2c4718585f7667abfd5ef81555338d6130bcb713d35308bd2fa88363a56480b34c40cc06acf51bc0481c2921cfe189c8452b4ea9b7efcff61f42eee821d72d11266010087e7bd51122cede8cc714a0e76a45eecc019b6aa9b3e161918dc5a8ff2dad048986",
        "Referrer-Policy": "strict-origin-when-cross-origin"
      },
      "body": null,
      "method": "GET"
    }).catch(err => {
      console.error('Error: ', err)
    })

    queryCount++
    console.info('Status:', response.status, '/', 'Total queries:', queryCount)
  }, x * 1000)

  setTimeout(() => {
    clearInterval(interval)
  }, y * 1000)
}

const oneMinInSec = 60
const oneHourInSec = oneMinInSec * 60
const fiveHoursInSec = oneHourInSec * 5

fetchHeatmapEveryXSecForYSec(oneMinInSec, fiveHoursInSec)



