#!/usr/bin/env node
/**
 * 天气查询脚本
 * 使用高德地图天气 API
 * 用法：node scripts/query.js --city=杭州 --type=forecast
 */

const { getWeather, getRealtimeWeather, formatWeather } = require('../index');

function parseArgs() {
  const args = {};
  process.argv.slice(2).forEach(arg => {
    const m = arg.slice(2).match(/^([^=]+)=(.*)$/);
    if (m) args[m[1]] = m[2];
  });
  return args;
}

async function main() {
  const args = parseArgs();
  const city = args.city || '杭州';
  const type = args.type || 'forecast';
  
  try {
    let result;
    
    if (type === 'realtime') {
      result = await getRealtimeWeather(city);
      console.log(`\n### 🌡️ ${result.city} 实时天气`);
      console.log(`\n更新时间：${result.reportTime}`);
      console.log(`天气：${result.weather}`);
      console.log(`温度：${result.temperature}°C`);
      console.log(`湿度：${result.humidity}%`);
      console.log(`风向：${result.windDirection} ${result.windPower}级\n`);
      
    } else {
      // forecast
      result = await getWeather(city);
      console.log('\n' + formatWeather(result));
      console.log('');
    }
    
  } catch (e) {
    console.error('❌ 查询失败:', e.message);
    console.log('\n提示：请确保已配置高德 API Key');
    console.log('  export AMAP_KEY=your_key');
    console.log('  或在 config.json 中设置 amapKey\n');
    process.exit(1);
  }
}

main();
