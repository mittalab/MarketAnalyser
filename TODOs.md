## 🔴 High Priority (Blocking)
- [ ] Add logging for debugging issues
- [ ] Expiry to give next month expiry even if month doesn't change and that is true for prev month as well
- [ ] Fetch future data from last date of data present in csv till today. Don't fetch if data present for today
- [ ] Fix FUT OI fetch from Fyers API
- [ ] Handle missing option chain data gracefully

## 🟡 Medium Priority (Important)
- [ ] Better logic to determine the change in Options OI trend, see `compute_daily_migration` func
- [ ] Persists and Refresh fyers token

## 🟢 Low Priority (Nice to Have)
- [ ] Add retry + timeout for API calls
