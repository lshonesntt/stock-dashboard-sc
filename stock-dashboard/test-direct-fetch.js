/* Direct Yahoo Finance fetch test - no dependencies */
console.log('Testing native fetch...');

async function test() {
  try {
    console.log('Fetching S&P 500...');
    const resp = await fetch(
      'https://query2.finance.yahoo.com/v7/finance/quote?symbols=%5EGSPC',
      {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(10000),
      }
    );
    
    console.log('Response status:', resp.status);
    const json = await resp.json();
    console.log('Keys:', Object.keys(json));
    console.log('Result:', JSON.stringify(json));
    
    if (json?.quoteSummary?.result?.[0]) {
      const quote = json.quoteSummary.result[0];
      console.log('Price:', quote.regularMarketPrice?.raw);
      console.log('Change:', quote.regularMarketChange?.raw);
    }
    console.log('✅ Success!');
  } catch (err) {
    console.error('❌ Error:', err.message);
    console.error('Stack:', err.stack);
  }
}

test();
