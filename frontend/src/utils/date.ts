export function getLocalDateString(date = new Date()) {
  // toISOString 使用 UTC；先扣掉时区偏移，得到浏览器本地日期。
  const offset = date.getTimezoneOffset() * 60 * 1000
  return new Date(date.getTime() - offset).toISOString().slice(0, 10)
}
