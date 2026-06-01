/* Simple Yahoo Finance fetch test */
async function test() {
  try {
    console.log('Testing Yahoo Finance API...');
    const resp = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1d&interval=1d', {
      headers: { 'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json' },
      redirect: 'follow',
      signal: AbortSignal.timeout(10000),
    });
    console.log('Status:', resp.status);
    const json = await resp.json();
    console.log('Keys:', Object.keys(json));
    const result = json?.chart?.result?.[0];
    console.log('Has result:', !!result);
    if (result) {
      const close = result?.indicators?.quote?.[0]?.close;
      console.log('Close array length:', close?.filter(v => v != null).length);
    }
    console.log('✅ Yahoo Finance API works!');
  } catch (err) {
    console.error('❌ Error:', err.message);
  }
}

test();
