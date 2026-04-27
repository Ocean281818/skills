#!/usr/bin/env node
/**
 * 天气服务 - 核心库
 * 使用高德地图天气 API
 * 参考：https://lbs.amap.com/api/webservice/guide/api/weatherinfo
 */

const fs = require('fs');
const path = require('path');
const axios = require('axios');

const CONFIG_FILE = path.join(__dirname, 'config.json');

/**
 * 读取配置
 */
function readConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    }
  } catch (e) {}
  return {};
}

/**
 * 获取高德 API Key
 */
function getApiKey() {
  const config = readConfig();
  return process.env.AMAP_KEY || config.amapKey;
}

/**
 * 确保 API Key 存在
 */
function ensureApiKey() {
  const key = getApiKey();
  if (!key) {
    throw new Error('请配置高德 API Key: export AMAP_KEY=xxx 或在 config.json 中设置 amapKey');
  }
  return key;
}

/**
 * 获取城市 ADCode
 * 高德天气 API 需要使用城市 ADCode（行政区划代码）
 */
async function getCityCode(city) {
  const key = ensureApiKey();
  
  // 使用地理编码 API 获取城市 ADCode
  const url = 'https://restapi.amap.com/v3/config/district';
  try {
    const res = await axios.get(url, {
      params: {
        key: key,
        keywords: city,
        subdistrict: 0,
        extensions: 'base'
      }
    });
    
    if (res.data.status === '1' && res.data.districts.length > 0) {
      return {
        adcode: res.data.districts[0].adcode,
        name: res.data.districts[0].name
      };
    }
    throw new Error(`未找到城市：${city}`);
  } catch (e) {
    throw new Error(`获取城市代码失败：${e.message}`);
  }
}

/**
 * 获取天气信息
 * @param {string} city 城市名称或 ADCode
 * @returns {Object} 天气数据
 */
async function getWeather(city) {
  const key = ensureApiKey();
  
  // 如果传入的是城市名，先获取 ADCode
  let adcode = city;
  let cityName = city;
  if (!/^\d{6}$/.test(city)) {
    const cityInfo = await getCityCode(city);
    adcode = cityInfo.adcode;
    cityName = cityInfo.name;
  }
  
  const url = 'https://restapi.amap.com/v3/weather/weatherInfo';
  
  try {
    const res = await axios.get(url, {
      params: {
        key: key,
        city: adcode,
        extensions: 'all'  // all=预报，base=实时
      }
    });
    
    if (res.data.status === '1') {
      const forecast = res.data.forecasts[0];
      return {
        city: forecast.city,
        adcode: forecast.adcode,
        reportTime: forecast.reportTime,
        casts: forecast.casts.map(c => ({
          date: c.date,
          dayWeather: c.dayweather,
          nightWeather: c.nightweather,
          dayTemp: c.daytemp,
          nightTemp: c.nighttemp,
          dayWind: c.daywind,
          nightWind: c.nightwind,
          dayPower: c.daypower,
          nightPower: c.nightpower
        }))
      };
    }
    throw new Error(`天气数据获取失败：${res.data.info}`);
  } catch (e) {
    throw new Error(`天气 API 请求失败：${e.message}`);
  }
}

/**
 * 获取实时天气
 */
async function getRealtimeWeather(city) {
  const key = ensureApiKey();
  
  let adcode = city;
  let cityName = city;
  if (!/^\d{6}$/.test(city)) {
    const cityInfo = await getCityCode(city);
    adcode = cityInfo.adcode;
    cityName = cityInfo.name;
  }
  
  const url = 'https://restapi.amap.com/v3/weather/weatherInfo';
  
  try {
    const res = await axios.get(url, {
      params: {
        key: key,
        city: adcode,
        extensions: 'base'  // base=实时
      }
    });
    
    if (res.data.status === '1' && res.data.lives.length > 0) {
      const live = res.data.lives[0];
      return {
        city: live.city,
        weather: live.weather,
        temperature: live.temperature,
        humidity: live.humidity,
        windDirection: live.winddirection,
        windPower: live.windpower,
        reportTime: live.reporttime
      };
    }
    throw new Error('实时天气数据获取失败');
  } catch (e) {
    throw new Error(`实时天气 API 请求失败：${e.message}`);
  }
}

/**
 * 分析天气并给出建议
 */
function analyzeWeather(cast) {
  const advice = [];
  const { dayWeather, dayTemp, nightTemp } = cast;
  
  if (dayTemp > 35) advice.push('⚠️ 高温：避开 12-15 点户外');
  if (nightTemp < 5) advice.push('🧥 低温：注意保暖');
  if (dayWeather.includes('雨')) advice.push('☔ 有雨：带伞，优先室内');
  if (dayWeather.includes('晴')) advice.push('☀️ 晴天：注意防晒');
  if (dayTemp - nightTemp > 10) advice.push(`🌡️ 温差大 (${nightTemp}°C~${dayTemp}°C)：建议带外套`);
  
  return advice;
}

/**
 * 格式化天气输出
 */
function formatWeather(weather) {
  const lines = [`### 🌤️ ${weather.city}天气预报 (${weather.reportTime})`];
  
  lines.push('\n| 日期 | 白天天气 | 夜间天气 | 温度 | 风向 |');
  lines.push('|------|---------|---------|------|------|');
  
  for (const cast of weather.casts) {
    const windInfo = `${cast.dayWind}风${cast.dayPower}级`;
    lines.push(`| ${cast.date} | ${cast.dayWeather} | ${cast.nightWeather} | ${cast.nightTemp}°C~${cast.dayTemp}°C | ${windInfo} |`);
  }
  
  lines.push('\n### 💡 出行建议');
  for (const cast of weather.casts) {
    const tips = analyzeWeather(cast);
    lines.push(`- ${cast.date}：${tips.join(' | ') || '适宜出行'}`);
  }
  
  return lines.join('\n');
}

module.exports = {
  readConfig,
  getApiKey,
  getCityCode,
  getWeather,
  getRealtimeWeather,
  analyzeWeather,
  formatWeather
};
