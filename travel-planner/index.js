#!/usr/bin/env node
/**
 * 智能旅游规划助手 - 核心库
 * 天气相关功能调用 weather-skill
 */

const fs = require('fs'), path = require('path'), axios = require('axios');
const CONFIG_FILE = path.join(__dirname, 'config.json');

// 尝试加载 weather-skill
let weatherSkill = null;
try {
  weatherSkill = require(process.env.WEATHER_SKILL_PATH || '/Users/ych/.hermes/skills/weather/index.js');
} catch (e) {
  console.log('⚠️  未找到 weather-skill，天气功能将不可用');
}

function readConfig() { try { if(fs.existsSync(CONFIG_FILE)) return JSON.parse(fs.readFileSync(CONFIG_FILE,'utf8')); } catch(e){} return {}; }
function getKeys() { const c=readConfig(); return { amapKey:process.env.AMAP_KEY||c.amapKey }; }
function ensureKeys() { const k=getKeys(); if(!k.amapKey) throw new Error('export AMAP_KEY=xxx'); return k; }

async function getWeather(city, days=3) {
  if (!weatherSkill) {
    console.log('⚠️  weather-skill 未加载，跳过天气分析');
    return null;
  }
  try {
    return await weatherSkill.getWeather(city, days);
  } catch (e) {
    console.log('⚠️  天气获取失败:', e.message);
    return null;
  }
}

function analyzeWeather(forecast) {
  if (!weatherSkill) return [];
  return weatherSkill.analyzeWeather(forecast);
}

async function searchPOI(p) {
  const {amapKey}=ensureKeys();
  try {
    const r=await axios.get('https://restapi.amap.com/v5/place/text',{params:{key:amapKey,keywords:p.keywords||'',region:p.city||'',offset:p.offset||5,appname:'travel-planner'}});
    return r.data.status==='1'?{success:true,pois:r.data.pois||[]}:{success:false,error:r.data.info};
  } catch(e) { return {success:false,error:e.message}; }
}

async function planRoute(orig,dest,city='',type='walking') {
  const {amapKey}=ensureKeys();
  const url=`https://restapi.amap.com/v3/direction/${type}`;
  const p={key:amapKey,origin:orig,destination:dest,appname:'travel-planner'};
  if(city&&type==='transfer') p.city=city;
  try { const r=await axios.get(url,{params:p}); return r.data.status==='1'?{success:true,data:r.data.route}:{success:false}; }
  catch(e) { return {success:false}; }
}

function isHoliday(d) { const x=new Date(d); return x.getDay()===0||x.getDay()===6; }
function assessCrowd(name,d) {
  const h=isHoliday(d);
  if(['迪士尼','外滩','西湖','故宫','长城'].some(k=>name.includes(k))) return h?'人山人海，早 8 前或晚 7 后':'人流较多';
  if(['夫子庙','灵隐寺','豫园'].some(k=>name.includes(k))) return h?'人流很多':'人流较多';
  return h?'人流较多':'人流适中';
}

function generateMapLink(data) { return `https://a.amap.com/jsapi_demo_show/static/openclaw/travel_plan.html?data=${encodeURIComponent(JSON.stringify(data))}`; }

async function planTravel({city,days=1,startDate=new Date().toISOString().split('T')[0],interests=['景点','美食']}) {
  console.log(`\n🗺️  规划${city}${days}日游...\n`);
  console.log('🌤️  获取天气...');
  const weather = await getWeather(city, days);
  if (weather) {
    console.log(`   ${weather.city}: ${weather.forecasts[0]?.textDay} ${weather.forecasts[0]?.tempMin}°C~${weather.forecasts[0]?.tempMax}°C`);
  }
  console.log('📍 搜索景点...');
  const mapData=[],pois={};
  for(const i of interests) {
    const r=await searchPOI({keywords:i,city});
    if(r.success&&r.pois.length) { pois[i]=r.pois; r.pois.forEach(p=>{const[lng,lat]=p.location.split(',');mapData.push({type:'poi',lnglat:[+lng,+lat],sort:i,text:p.name});}); }
  }
  const all=Object.values(pois).flat(),itinerary=[];
  for(let d=0;d<days;d++) {
    const dp={day:d+1,date:new Date(new Date(startDate).getTime()+d*864e5).toISOString().split('T')[0],weather:weather?.forecasts?.[d],advice:weather?.forecasts?.[d]?analyzeWeather(weather.forecasts[d]):[],activities:[]};
    const perDay=Math.ceil(all.length/days),dayPois=all.slice(d*perDay,(d+1)*perDay);
    for(const p of dayPois) { const[lng,lat]=p.location.split(',');dp.activities.push({name:p.name,type:p.type,location:p.location,lnglat:[+lng,+lat],crowd:assessCrowd(p.name,dp.date)}); }
    if(pois['美食']) dp.meals=pois['美食'].slice(0,3).map(m=>({name:m.name,address:m.address}));
    itinerary.push(dp);
  }
  console.log('🛣️  规划路线...');
  for(let d=0;d<itinerary.length;d++) {
    const a=itinerary[d].activities;
    for(let i=0;i<a.length-1;i++) mapData.push({type:'route',routeType:'walking',start:a[i].lnglat,end:a[i+1].lnglat});
  }
  return {itinerary,mapLink:generateMapLink(mapData),weather};
}

module.exports={readConfig,getWeather,analyzeWeather,searchPOI,planRoute,assessCrowd,generateMapLink,planTravel};
