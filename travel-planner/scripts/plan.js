#!/usr/bin/env node
/**
 * 智能旅游规划主程序
 * 用法：node scripts/plan.js --city=杭州 --days=3 --startDate=2024-05-01
 */

const { planTravel, generateMapLink } = require('../index');

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
  if (!args.city) {
    console.log('用法：node plan.js --city=城市 [--days=天数] [--startDate=日期] [--interests=兴趣]');
    console.log('示例：node plan.js --city=杭州 --days=3 --interests=景点，美食，酒店');
    process.exit(1);
  }
  
  const days = parseInt(args.days) || 1;
  const startDate = args.startDate || new Date().toISOString().split('T')[0];
  const interests = args.interests ? args.interests.split(',') : ['景点', '美食'];
  
  try {
    const result = await planTravel({ city: args.city, days, startDate, interests });
    
    // 输出精简版行程
    console.log('\n' + '='.repeat(60));
    for (const day of result.itinerary) {
      console.log(`\n## Day ${day.day}：${day.date}`);
      if (day.weather) {
        console.log(`🌤️ ${day.weather.textDay} ${day.weather.tempMin}°C~${day.weather.tempMax}°C`);
        if (day.advice.length) console.log(`   ${day.advice.join(' | ')}`);
      }
      if (day.activities.length) {
        console.log('\n📍 行程:');
        day.activities.forEach((a, i) => {
          console.log(`   ${i+1}. ${a.name} (${a.crowd})`);
        });
      }
      if (day.meals?.length) {
        console.log('\n🍜 美食:');
        day.meals.forEach(m => console.log(`   - ${m.name}`));
      }
    }
    console.log('\n' + '='.repeat(60));
    console.log(`\n🗺️  地图链接：${result.mapLink}\n`);
    
  } catch (e) {
    console.error('❌ 错误:', e.message);
    process.exit(1);
  }
}

main();
