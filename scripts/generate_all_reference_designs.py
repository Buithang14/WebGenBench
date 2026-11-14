"""scripts/generate_all_reference_designs.py
Tạo bộ ảnh thiết kế mẫu gốc (Design Reference / Ground Truth) chuẩn 1440x900px
cho toàn bộ 8 bài tập Benchmark (T01 - T08) sử dụng Playwright và HTML5/CSS3 chuẩn hiện đại.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

DESIGNS_DIR = Path("d:/WebGenBench/designs")
DESIGNS_DIR.mkdir(parents=True, exist_ok=True)

SHARED_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #F8FAFC;
    color: #0F172A;
    width: 1440px;
    height: 900px;
    overflow: hidden;
    position: relative;
    -webkit-font-smoothing: antialiased;
}
input, button, select, textarea { font-family: inherit; }
"""

# HTML Templates for all 8 tasks
TEMPLATES = {
    "T01": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: radial-gradient(circle at 50% 30%, #EEF2F6 0%, #E2E8F0 100%);
}
.card {
    background: #FFFFFF;
    width: 480px;
    padding: 48px 44px;
    border-radius: 20px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
    border: 1px solid #E2E8F0;
}
.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 28px;
}
.brand-logo {
    width: 36px;
    height: 36px;
    background: #0B57D0;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 18px;
}
.brand-name {
    font-weight: 700;
    font-size: 19px;
    color: #0F172A;
}
h1 {
    font-size: 26px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}
p.subtitle {
    font-size: 14px;
    color: #64748B;
    margin-bottom: 28px;
}
.form-group {
    margin-bottom: 20px;
}
label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 8px;
}
.input-box {
    position: relative;
    display: flex;
    align-items: center;
}
input[type="email"], input[type="password"] {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    font-size: 14px;
    background: #F8FAFC;
    color: #0F172A;
    outline: none;
    transition: all 0.2s;
}
.eye-btn {
    position: absolute;
    right: 14px;
    background: none;
    border: none;
    color: #64748B;
    cursor: pointer;
    display: flex;
    align-items: center;
}
.options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    margin: 20px 0 28px 0;
}
.remember {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #475569;
    cursor: pointer;
}
.remember input {
    accent-color: #0B57D0;
    width: 16px;
    height: 16px;
    border-radius: 4px;
}
.forgot-link {
    color: #0B57D0;
    text-decoration: none;
    font-weight: 600;
}
.btn-submit {
    width: 100%;
    padding: 13px;
    background: #0B57D0;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(11, 87, 208, 0.25);
}
.footer-text {
    text-align: center;
    font-size: 13px;
    color: #64748B;
    margin-top: 24px;
}
.footer-text a {
    color: #0B57D0;
    text-decoration: none;
    font-weight: 600;
}
</style>
</head>
<body>
<div class="wrapper">
    <div class="card">
        <div class="brand">
            <div class="brand-logo">W</div>
            <div class="brand-name">WebGenBench</div>
        </div>
        <h1>Welcome Back</h1>
        <p class="subtitle">Please enter your credentials to access your dashboard.</p>
        
        <div class="form-group">
            <label>Email Address</label>
            <div class="input-box">
                <input type="email" value="alex.morgan@company.com" placeholder="name@company.com">
            </div>
        </div>

        <div class="form-group">
            <label>Password</label>
            <div class="input-box">
                <input type="password" value="SuperSecretPassword123!">
                <button class="eye-btn" type="button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                </button>
            </div>
        </div>

        <div class="options">
            <label class="remember"><input type="checkbox" checked> Remember for 30 days</label>
            <a href="#" class="forgot-link">Forgot password?</a>
        </div>

        <button class="btn-submit" type="button">Sign In</button>

        <div class="footer-text">
            Don't have an account? <a href="#">Create account</a>
        </div>
    </div>
</div>
</body>
</html>
""",

    "T02": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: radial-gradient(circle at 50% 30%, #EEF2F6 0%, #E2E8F0 100%);
}
.card {
    background: #FFFFFF;
    width: 520px;
    padding: 38px 42px;
    border-radius: 20px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
    border: 1px solid #E2E8F0;
}
.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
}
.brand-logo {
    width: 32px;
    height: 32px;
    background: #0B57D0;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 16px;
}
.brand-name {
    font-weight: 700;
    font-size: 18px;
    color: #0F172A;
}
h1 {
    font-size: 24px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}
p.subtitle {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 22px;
}
.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 14px;
}
.form-group {
    margin-bottom: 14px;
}
label {
    display: block;
    font-size: 12.5px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 6px;
}
.input-box {
    position: relative;
    display: flex;
    align-items: center;
}
input[type="text"], input[type="email"], input[type="password"], input[type="tel"] {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    font-size: 13.5px;
    background: #F8FAFC;
    color: #0F172A;
    outline: none;
}
.eye-btn {
    position: absolute;
    right: 12px;
    background: none;
    border: none;
    color: #64748B;
    cursor: pointer;
    display: flex;
}
.strength-bar-wrap {
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.strength-bar {
    display: flex;
    gap: 4px;
    flex: 1;
}
.strength-seg {
    height: 4px;
    flex: 1;
    border-radius: 2px;
    background: #E2E8F0;
}
.strength-seg.active {
    background: #10B981;
}
.strength-text {
    font-size: 11px;
    font-weight: 600;
    color: #10B981;
}
.terms {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12.5px;
    color: #475569;
    margin: 18px 0 22px 0;
    line-height: 1.4;
}
.terms input {
    margin-top: 2px;
    accent-color: #0B57D0;
}
.terms a {
    color: #0B57D0;
    text-decoration: none;
    font-weight: 600;
}
.btn-submit {
    width: 100%;
    padding: 12px;
    background: #0B57D0;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(11, 87, 208, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
.footer-text {
    text-align: center;
    font-size: 12.5px;
    color: #64748B;
    margin-top: 18px;
}
.footer-text a {
    color: #0B57D0;
    text-decoration: none;
    font-weight: 600;
}
</style>
</head>
<body>
<div class="wrapper">
    <div class="card">
        <div class="brand">
            <div class="brand-logo">W</div>
            <div class="brand-name">WebGenBench</div>
        </div>
        <h1>Create an Account</h1>
        <p class="subtitle">Join thousands of developers benchmarking code generation.</p>
        
        <div class="form-grid">
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" value="Nguyen Van An">
            </div>
            <div class="form-group">
                <label>Phone Number</label>
                <input type="tel" value="0912 345 678">
            </div>
        </div>

        <div class="form-group">
            <label>Work Email</label>
            <input type="email" value="an.nguyen@university.edu.vn">
        </div>

        <div class="form-group">
            <label>Password</label>
            <div class="input-box">
                <input type="password" value="PassStrong2026!@#">
                <button class="eye-btn" type="button">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                </button>
            </div>
            <div class="strength-bar-wrap">
                <div class="strength-bar">
                    <div class="strength-seg active"></div>
                    <div class="strength-seg active"></div>
                    <div class="strength-seg active"></div>
                    <div class="strength-seg active"></div>
                </div>
                <span class="strength-text">Strong password</span>
            </div>
        </div>

        <div class="form-group">
            <label>Confirm Password</label>
            <div class="input-box">
                <input type="password" value="PassStrong2026!@#">
                <button class="eye-btn" type="button">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                </button>
            </div>
        </div>

        <label class="terms">
            <input type="checkbox" checked>
            <span>I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.</span>
        </label>

        <button class="btn-submit" type="button">Register Account</button>

        <div class="footer-text">
            Already have an account? <a href="#">Log in</a>
        </div>
    </div>
</div>
</body>
</html>
""",

    "T03": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.layout {
    display: flex;
    height: 100vh;
}
.sidebar {
    width: 260px;
    background: #0F172A;
    color: white;
    padding: 28px 20px;
    display: flex;
    flex-direction: column;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 36px;
    padding-left: 8px;
}
.sidebar-brand-logo {
    width: 34px;
    height: 34px;
    background: #3B82F6;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}
.sidebar-brand-name {
    font-size: 18px;
    font-weight: 700;
}
.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 10px;
    color: #94A3B8;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
}
.nav-item.active {
    background: #1E293B;
    color: #FFFFFF;
    font-weight: 600;
}
.main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    background: #F8FAFC;
}
.header {
    height: 72px;
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 36px;
}
.search-bar {
    width: 360px;
    padding: 9px 16px 9px 38px;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    font-size: 13.5px;
    background: #F8FAFC;
    position: relative;
}
.search-wrap {
    position: relative;
    display: flex;
    align-items: center;
}
.search-icon {
    position: absolute;
    left: 12px;
    color: #94A3B8;
}
.user-profile {
    display: flex;
    align-items: center;
    gap: 14px;
}
.avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: #3B82F6;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
}
.content {
    padding: 32px 36px;
}
.page-title {
    font-size: 24px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 6px;
}
.page-subtitle {
    font-size: 14px;
    color: #64748B;
    margin-bottom: 24px;
}
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 28px;
}
.metric-card {
    background: #FFFFFF;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.metric-label {
    font-size: 13px;
    color: #64748B;
    font-weight: 600;
}
.metric-badge {
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 20px;
    font-weight: 600;
    background: #DCFCE7;
    color: #15803D;
}
.metric-value {
    font-size: 26px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 6px;
}
.metric-sub {
    font-size: 12px;
    color: #94A3B8;
}
.chart-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
}
.panel {
    background: #FFFFFF;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.panel-title {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 18px;
}
.bar-chart-mock {
    height: 220px;
    display: flex;
    align-items: flex-end;
    gap: 22px;
    padding-bottom: 8px;
    border-bottom: 1px solid #E2E8F0;
}
.bar-col {
    flex: 1;
    height: 185px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    gap: 10px;
}
.bar-track {
    width: 100%;
    height: 155px;
    display: flex;
    align-items: flex-end;
}
.bar-fill {
    width: 100%;
    border-radius: 6px 6px 0 0;
    background: #3B82F6;
}
.bar-label {
    font-size: 12px;
    color: #64748B;
}
.table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.table th {
    text-align: left;
    color: #64748B;
    font-weight: 600;
    padding-bottom: 12px;
    border-bottom: 1px solid #E2E8F0;
}
.table td {
    padding: 12px 0;
    border-bottom: 1px solid #F1F5F9;
    color: #334155;
}
</style>
</head>
<body>
<div class="layout">
    <div class="sidebar">
        <div class="sidebar-brand">
            <div class="sidebar-brand-logo">W</div>
            <div class="sidebar-brand-name">WebAnalytics</div>
        </div>
        <a href="#" class="nav-item active">📊 Dashboard</a>
        <a href="#" class="nav-item">📈 Performance</a>
        <a href="#" class="nav-item">👥 Users & Traffic</a>
        <a href="#" class="nav-item">🛒 Conversion</a>
        <a href="#" class="nav-item">⚙️ Settings</a>
    </div>

    <div class="main">
        <div class="header">
            <div class="search-wrap">
                <span class="search-icon">🔍</span>
                <input type="text" class="search-bar" placeholder="Search metrics, reports or logs...">
            </div>
            <div class="user-profile">
                <div style="text-align:right;">
                    <div style="font-size:13.5px; font-weight:700; color:#0F172A;">Dr. Sarah Jenkins</div>
                    <div style="font-size:11.5px; color:#64748B;">Lead Researcher</div>
                </div>
                <div class="avatar">SJ</div>
            </div>
        </div>

        <div class="content">
            <div class="page-title">Executive Performance KPI</div>
            <div class="page-subtitle">Real-time metrics aggregated across all experiment benchmarks.</div>

            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">TOTAL REVENUE</span>
                        <span class="metric-badge">+18.2%</span>
                    </div>
                    <div class="metric-value">$128,450</div>
                    <div class="metric-sub">vs. $108,600 last month</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">ACTIVE USERS</span>
                        <span class="metric-badge">+12.4%</span>
                    </div>
                    <div class="metric-value">48,290</div>
                    <div class="metric-sub">Daily active sessions</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">CONVERSION RATE</span>
                        <span class="metric-badge">+3.8%</span>
                    </div>
                    <div class="metric-value">4.28%</div>
                    <div class="metric-sub">Checkout funnel rate</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">TOTAL RUNS</span>
                        <span class="metric-badge" style="background:#EFF6FF; color:#1D4ED8;">144/144</span>
                    </div>
                    <div class="metric-value">1,894</div>
                    <div class="metric-sub">Pass rate 99.4%</div>
                </div>
            </div>

            <div class="chart-grid">
                <div class="panel">
                    <div class="panel-title">Weekly Code Synthesis Throughput</div>
                    <div class="bar-chart-mock">
                        <div class="bar-col">
                            <div class="bar-track"><div class="bar-fill" style="height: 105px;"></div></div>
                            <span class="bar-label">Mon</span>
                        </div>
                        <div class="bar-col">
                            <div class="bar-track"><div class="bar-fill" style="height: 135px;"></div></div>
                            <span class="bar-label">Tue</span>
                        </div>
                        <div class="bar-col">
                            <div class="bar-track"><div class="bar-fill" style="height: 80px;"></div></div>
                            <span class="bar-label">Wed</span>
                        </div>
                        <div class="bar-col">
                            <div class="bar-track"><div class="bar-fill" style="height: 150px; background:#0B57D0;"></div></div>
                            <span class="bar-label">Thu</span>
                        </div>
                        <div class="bar-col">
                            <div class="bar-track"><div class="bar-fill" style="height: 115px;"></div></div>
                            <span class="bar-label">Fri</span>
                        </div>
                        <div class="bar-col">
                            <div class="bar-track"><div class="bar-fill" style="height: 65px;"></div></div>
                            <span class="bar-label">Sat</span>
                        </div>
                        <div class="bar-col">
                            <div class="bar-track"><div class="bar-fill" style="height: 45px;"></div></div>
                            <span class="bar-label">Sun</span>
                        </div>
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-title">Recent Run Logs</div>
                    <table class="table">
                        <thead>
                            <tr><th>Run</th><th>IDE</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>#001</td><td>Cursor</td><td><span style="color:#10B981; font-weight:600;">PASS (92đ)</span></td></tr>
                            <tr><td>#002</td><td>Windsurf</td><td><span style="color:#10B981; font-weight:600;">PASS (89đ)</span></td></tr>
                            <tr><td>#003</td><td>VS Code</td><td><span style="color:#10B981; font-weight:600;">PASS (84đ)</span></td></tr>
                            <tr><td>#004</td><td>Cursor</td><td><span style="color:#10B981; font-weight:600;">PASS (95đ)</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
""",

    "T04": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.navbar {
    height: 72px;
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 0 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand {
    font-size: 22px;
    font-weight: 800;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 10px;
}
.brand span { color: #0B57D0; }
.cart-badge {
    background: #0B57D0;
    color: white;
    padding: 8px 18px;
    border-radius: 9999px;
    font-size: 13.5px;
    font-weight: 600;
}
.container {
    padding: 36px 60px;
}
.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
}
.filters {
    display: flex;
    gap: 10px;
}
.filter-btn {
    padding: 8px 18px;
    border-radius: 9999px;
    border: 1px solid #CBD5E1;
    background: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
}
.filter-btn.active {
    background: #0B57D0;
    color: white;
    border-color: #0B57D0;
}
.sort-select {
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid #CBD5E1;
    font-size: 13px;
    background: white;
    color: #334155;
    outline: none;
}
.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
}
.card {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    position: relative;
    display: flex;
    flex-direction: column;
}
.badge {
    position: absolute;
    top: 14px;
    left: 14px;
    background: #EF4444;
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    z-index: 2;
}
.img-placeholder {
    height: 190px;
    background: #F1F5F9;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    color: #94A3B8;
}
.card-body {
    padding: 18px;
    display: flex;
    flex-direction: column;
    flex: 1;
}
.category {
    font-size: 11.5px;
    color: #64748B;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.title {
    font-size: 15px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 8px;
    line-height: 1.35;
}
.rating {
    font-size: 12px;
    color: #F59E0B;
    margin-bottom: 14px;
}
.price-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-top: auto;
    margin-bottom: 14px;
}
.curr-price {
    font-size: 18px;
    font-weight: 800;
    color: #0F172A;
}
.old-price {
    font-size: 13px;
    color: #94A3B8;
    text-decoration: line-through;
}
.btn-cart {
    width: 100%;
    padding: 10px;
    background: #0B57D0;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
}
</style>
</head>
<body>
<div class="navbar">
    <div class="brand">Lumina<span>Shop</span></div>
    <div class="cart-badge">🛒 Cart (3 items)</div>
</div>

<div class="container">
    <div class="header-row">
        <div class="filters">
            <button class="filter-btn active">All Items</button>
            <button class="filter-btn">Headphones</button>
            <button class="filter-btn">Smartwatches</button>
            <button class="filter-btn">Laptops & Accessories</button>
        </div>
        <select class="sort-select">
            <option>Sort by: Featured</option>
            <option>Price: Low to High</option>
            <option>Price: High to Low</option>
            <option>Customer Rating</option>
        </select>
    </div>

    <div class="grid">
        <div class="card">
            <span class="badge">-25% OFF</span>
            <div class="img-placeholder">🎧</div>
            <div class="card-body">
                <span class="category">Audio Equipment</span>
                <div class="title">Wireless Noise-Canceling Studio Pro Headphones</div>
                <div class="rating">★★★★★ (142 reviews)</div>
                <div class="price-row">
                    <span class="curr-price">$179.99</span>
                    <span class="old-price">$239.99</span>
                </div>
                <button class="btn-cart">Add to Cart</button>
            </div>
        </div>

        <div class="card">
            <span class="badge" style="background:#10B981;">HOT NEW</span>
            <div class="img-placeholder">⌚</div>
            <div class="card-body">
                <span class="category">Wearables</span>
                <div class="title">Fitness Tracker Pro with Heart Rate & GPS</div>
                <div class="rating">★★★★☆ (89 reviews)</div>
                <div class="price-row">
                    <span class="curr-price">$129.00</span>
                    <span class="old-price">$159.00</span>
                </div>
                <button class="btn-cart">Add to Cart</button>
            </div>
        </div>

        <div class="card">
            <span class="badge">-15% OFF</span>
            <div class="img-placeholder">💻</div>
            <div class="card-body">
                <span class="category">Computers</span>
                <div class="title">Ultra-Slim Aluminum Laptop Stand & Hub</div>
                <div class="rating">★★★★★ (215 reviews)</div>
                <div class="price-row">
                    <span class="curr-price">$59.50</span>
                    <span class="old-price">$70.00</span>
                </div>
                <button class="btn-cart">Add to Cart</button>
            </div>
        </div>

        <div class="card">
            <span class="badge">-30% OFF</span>
            <div class="img-placeholder">⌨️</div>
            <div class="card-body">
                <span class="category">Accessories</span>
                <div class="title">Mechanical RGB Gaming Keyboard (Tactile Brown)</div>
                <div class="rating">★★★★☆ (64 reviews)</div>
                <div class="price-row">
                    <span class="curr-price">$89.99</span>
                    <span class="old-price">$129.99</span>
                </div>
                <button class="btn-cart">Add to Cart</button>
            </div>
        </div>
    </div>
</div>
</body>
</html>
""",

    "T05": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.wrapper {
    padding: 60px 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.header {
    text-align: center;
    max-width: 640px;
    margin-bottom: 36px;
}
.badge-tag {
    background: #DBEAFE;
    color: #1D4ED8;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 9999px;
    display: inline-block;
    margin-bottom: 12px;
}
h1 {
    font-size: 34px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
}
p.subtitle {
    font-size: 15px;
    color: #64748B;
    line-height: 1.5;
}
.toggle-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #F1F5F9;
    padding: 6px;
    border-radius: 9999px;
    margin-bottom: 44px;
}
.toggle-btn {
    padding: 8px 20px;
    border-radius: 9999px;
    border: none;
    font-size: 13.5px;
    font-weight: 600;
    color: #64748B;
    background: none;
    cursor: pointer;
}
.toggle-btn.active {
    background: #FFFFFF;
    color: #0F172A;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}
.save-badge {
    background: #DCFCE7;
    color: #15803D;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 9999px;
}
.pricing-grid {
    display: grid;
    grid-template-columns: repeat(3, 360px);
    gap: 28px;
    align-items: stretch;
}
.price-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 36px 32px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
    position: relative;
}
.price-card.popular {
    border: 2px solid #0B57D0;
    box-shadow: 0 10px 25px -5px rgba(11, 87, 208, 0.15);
    transform: translateY(-8px);
}
.popular-banner {
    position: absolute;
    top: -14px;
    left: 50%;
    transform: translateX(-50%);
    background: #0B57D0;
    color: white;
    font-size: 11.5px;
    font-weight: 700;
    padding: 4px 16px;
    border-radius: 9999px;
    letter-spacing: 0.3px;
}
.card-tier {
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 6px;
}
.card-desc {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 24px;
}
.price-amount {
    display: flex;
    align-items: baseline;
    gap: 4px;
    margin-bottom: 24px;
}
.price-num {
    font-size: 42px;
    font-weight: 800;
    color: #0F172A;
}
.price-period {
    font-size: 14px;
    color: #64748B;
}
.feature-list {
    list-style: none;
    margin-bottom: 32px;
    flex: 1;
}
.feature-item {
    font-size: 13.5px;
    color: #334155;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.check-icon {
    color: #10B981;
    font-weight: 800;
}
.btn-tier {
    width: 100%;
    padding: 13px;
    border-radius: 10px;
    border: 1px solid #CBD5E1;
    background: #FFFFFF;
    color: #0F172A;
    font-size: 14.5px;
    font-weight: 600;
    cursor: pointer;
}
.btn-tier.primary {
    background: #0B57D0;
    color: white;
    border: none;
    box-shadow: 0 4px 12px rgba(11, 87, 208, 0.25);
}
</style>
</head>
<body>
<div class="wrapper">
    <div class="header">
        <span class="badge-tag">TRANSPARENT PRICING</span>
        <h1>Flexible Plans for Teams of All Sizes</h1>
        <p class="subtitle">Deploy your AI benchmark pipelines with full confidence. Upgrade or cancel anytime.</p>
    </div>

    <div class="toggle-wrap">
        <button class="toggle-btn">Monthly billing</button>
        <button class="toggle-btn active">Annual billing <span class="save-badge">Save 20%</span></button>
    </div>

    <div class="pricing-grid">
        <div class="price-card">
            <div class="card-tier">Starter</div>
            <div class="card-desc">Ideal for individual developers & small projects.</div>
            <div class="price-amount"><span class="price-num">$19</span><span class="price-period">/ month</span></div>
            <ul class="feature-list">
                <li class="feature-item"><span class="check-icon">✓</span> Up to 5 benchmark tasks</li>
                <li class="feature-item"><span class="check-icon">✓</span> 50 AI code executions/mo</li>
                <li class="feature-item"><span class="check-icon">✓</span> Standard 6-metric evaluation</li>
                <li class="feature-item"><span class="check-icon">✓</span> Community Discord support</li>
            </ul>
            <button class="btn-tier">Start Free 14-day Trial</button>
        </div>

        <div class="price-card popular">
            <span class="popular-banner">MOST POPULAR</span>
            <div class="card-tier">Professional</div>
            <div class="card-desc">For research labs & scaling engineering teams.</div>
            <div class="price-amount"><span class="price-num">$49</span><span class="price-period">/ month</span></div>
            <ul class="feature-list">
                <li class="feature-item"><span class="check-icon">✓</span> Unlimited benchmark tasks</li>
                <li class="feature-item"><span class="check-icon">✓</span> 500 AI executions/mo</li>
                <li class="feature-item"><span class="check-icon">✓</span> Multi-viewport (Desktop, Tab, Mob)</li>
                <li class="feature-item"><span class="check-icon">✓</span> Blind review & Fleiss' Kappa</li>
                <li class="feature-item"><span class="check-icon">✓</span> Priority email & chat support</li>
            </ul>
            <button class="btn-tier primary">Get Started Now</button>
        </div>

        <div class="price-card">
            <div class="card-tier">Enterprise</div>
            <div class="card-desc">Custom infrastructure & high-concurrency needs.</div>
            <div class="price-amount"><span class="price-num">$99</span><span class="price-period">/ month</span></div>
            <ul class="feature-list">
                <li class="feature-item"><span class="check-icon">✓</span> Custom IDE adapters & runner</li>
                <li class="feature-item"><span class="check-icon">✓</span> Dedicated cloud batch runner</li>
                <li class="feature-item"><span class="check-icon">✓</span> Automated thesis PDF export</li>
                <li class="feature-item"><span class="check-icon">✓</span> 99.9% uptime SLA</li>
                <li class="feature-item"><span class="check-icon">✓</span> Dedicated account manager</li>
            </ul>
            <button class="btn-tier">Contact Sales</button>
        </div>
    </div>
</div>
</body>
</html>
""",

    "T06": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.wrapper {
    max-width: 980px;
    margin: 40px auto;
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
    overflow: hidden;
}
.cover-banner {
    height: 160px;
    background: linear-gradient(135deg, #0B57D0 0%, #00639B 50%, #001D35 100%);
    position: relative;
}
.profile-header {
    padding: 0 44px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: -50px;
    margin-bottom: 24px;
    position: relative;
    z-index: 2;
}
.avatar-wrap {
    display: flex;
    align-items: flex-end;
    gap: 20px;
}
.avatar-img {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 4px solid #FFFFFF;
    background: #3B82F6;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    font-weight: 700;
    box-shadow: 0 4px 6px rgba(0,0,0,0.08);
}
.user-info h2 {
    font-size: 22px;
    font-weight: 700;
    color: #0F172A;
}
.user-info p {
    font-size: 13.5px;
    color: #64748B;
}
.btn-change-avatar {
    padding: 8px 16px;
    border: 1px solid #CBD5E1;
    background: white;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #334155;
    cursor: pointer;
}
.tabs-bar {
    display: flex;
    border-bottom: 1px solid #E2E8F0;
    padding: 0 44px;
    gap: 32px;
}
.tab-link {
    padding: 14px 0;
    font-size: 14px;
    font-weight: 600;
    color: #64748B;
    text-decoration: none;
    border-bottom: 2px solid transparent;
}
.tab-link.active {
    color: #0B57D0;
    border-bottom-color: #0B57D0;
}
.form-content {
    padding: 32px 44px;
}
.form-grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}
.form-group {
    margin-bottom: 20px;
}
label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 8px;
}
input[type="text"], input[type="email"], select, textarea {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    font-size: 14px;
    background: #F8FAFC;
    color: #0F172A;
    outline: none;
}
textarea {
    resize: none;
    height: 80px;
}
.actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 10px;
    padding-top: 20px;
    border-top: 1px solid #E2E8F0;
}
.btn-cancel {
    padding: 10px 20px;
    border: 1px solid #CBD5E1;
    background: white;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
}
.btn-save {
    padding: 10px 22px;
    border: none;
    background: #0B57D0;
    color: white;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(11, 87, 208, 0.25);
}
</style>
</head>
<body>
<div class="wrapper">
    <div class="cover-banner"></div>
    <div class="profile-header">
        <div class="avatar-wrap">
            <div class="avatar-img">JD</div>
            <div class="user-info">
                <h2>Johnathan Doe</h2>
                <p>Senior AI Engineer &amp; Benchmark Lead</p>
            </div>
        </div>
        <button class="btn-change-avatar" type="button">Change Avatar</button>
    </div>

    <div class="tabs-bar">
        <a href="#" class="tab-link active">Personal Information</a>
        <a href="#" class="tab-link">Password &amp; Security</a>
        <a href="#" class="tab-link">Notifications</a>
        <a href="#" class="tab-link">API Keys &amp; Integrations</a>
    </div>

    <div class="form-content">
        <div class="form-grid-2">
            <div class="form-group">
                <label>First Name</label>
                <input type="text" value="Johnathan">
            </div>
            <div class="form-group">
                <label>Last Name</label>
                <input type="text" value="Doe">
            </div>
        </div>

        <div class="form-grid-2">
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" value="johnathan.doe@benchmark-ai.org">
            </div>
            <div class="form-group">
                <label>Timezone</label>
                <select>
                    <option>(GMT+07:00) Hanoi, Bangkok, Jakarta</option>
                    <option>(GMT-08:00) Pacific Time (US & Canada)</option>
                    <option>(GMT+00:00) UTC / London</option>
                </select>
            </div>
        </div>

        <div class="form-group">
            <label>Biography</label>
            <textarea>Evaluating LLM-based autonomous coding agents across multi-turn responsive UI generation.</textarea>
        </div>

        <div class="actions">
            <button class="btn-cancel" type="button">Cancel</button>
            <button class="btn-save" type="button">Save Changes</button>
        </div>
    </div>
</div>
</body>
</html>
""",

    "T07": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.navbar {
    height: 64px;
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 0 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand {
    font-size: 20px;
    font-weight: 800;
    color: #0F172A;
}
.brand span { color: #0B57D0; }
.secure-badge {
    font-size: 13px;
    color: #10B981;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}
.container {
    max-width: 1140px;
    margin: 32px auto;
}
.wizard-stepper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 36px;
    gap: 24px;
}
.step {
    display: flex;
    align-items: center;
    gap: 10px;
}
.step-num {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #E2E8F0;
    color: #64748B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
}
.step.active .step-num {
    background: #0B57D0;
    color: white;
}
.step-text {
    font-size: 13.5px;
    font-weight: 600;
    color: #64748B;
}
.step.active .step-text {
    color: #0F172A;
}
.step-divider {
    width: 60px;
    height: 2px;
    background: #E2E8F0;
}
.step-divider.active {
    background: #0B57D0;
}
.layout-2col {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 32px;
}
.panel {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    padding: 32px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.panel-title {
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.form-grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
}
.form-group {
    margin-bottom: 16px;
}
label {
    display: block;
    font-size: 12.5px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 6px;
}
input, select {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    font-size: 13.5px;
    background: #F8FAFC;
    color: #0F172A;
    outline: none;
}
.wizard-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #E2E8F0;
}
.btn-back {
    padding: 11px 22px;
    border: 1px solid #CBD5E1;
    background: white;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
}
.btn-continue {
    padding: 11px 26px;
    border: none;
    background: #0B57D0;
    color: white;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(11, 87, 208, 0.25);
}
.order-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    font-size: 13.5px;
}
.order-item-name {
    color: #334155;
    font-weight: 500;
}
.order-item-price {
    font-weight: 700;
    color: #0F172A;
}
.summary-line {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #64748B;
    margin-bottom: 8px;
}
.summary-line.total {
    border-top: 1px solid #E2E8F0;
    padding-top: 14px;
    margin-top: 14px;
    font-size: 16px;
    font-weight: 800;
    color: #0F172A;
}
</style>
</head>
<body>
<div class="navbar">
    <div class="brand">Apex<span>Checkout</span></div>
    <div class="secure-badge">🔒 256-Bit SSL Encrypted</div>
</div>

<div class="container">
    <div class="wizard-stepper">
        <div class="step active">
            <div class="step-num">1</div>
            <div class="step-text">Shipping Address</div>
        </div>
        <div class="step-divider active"></div>
        <div class="step">
            <div class="step-num">2</div>
            <div class="step-text">Payment Method</div>
        </div>
        <div class="step-divider"></div>
        <div class="step">
            <div class="step-num">3</div>
            <div class="step-text">Order Review</div>
        </div>
    </div>

    <div class="layout-2col">
        <div class="panel">
            <div class="panel-title">1. Shipping Information</div>
            
            <div class="form-grid-2">
                <div class="form-group">
                    <label>First Name</label>
                    <input type="text" value="An">
                </div>
                <div class="form-group">
                    <label>Last Name</label>
                    <input type="text" value="Nguyen">
                </div>
            </div>

            <div class="form-group">
                <label>Street Address</label>
                <input type="text" value="144 Xuan Thuy Street">
            </div>

            <div class="form-grid-2">
                <div class="form-group">
                    <label>City / District</label>
                    <input type="text" value="Cau Giay, Hanoi">
                </div>
                <div class="form-group">
                    <label>Postal Code</label>
                    <input type="text" value="100000">
                </div>
            </div>

            <div class="form-group">
                <label>Delivery Method</label>
                <select>
                    <option>Standard Express (2-3 business days) - FREE</option>
                    <option>Next-day Priority Delivery - $12.00</option>
                </select>
            </div>

            <div class="wizard-actions">
                <button class="btn-back" type="button">Return to Cart</button>
                <button class="btn-continue" type="button">Continue to Payment →</button>
            </div>
        </div>

        <div class="panel" style="height: fit-content;">
            <div class="panel-title">Order Summary</div>
            <div class="order-item">
                <span class="order-item-name">Studio Headphones (x1)</span>
                <span class="order-item-price">$179.99</span>
            </div>
            <div class="order-item">
                <span class="order-item-name">Mechanical Keyboard (x1)</span>
                <span class="order-item-price">$89.99</span>
            </div>
            
            <div style="margin: 20px 0; border-top: 1px solid #E2E8F0;"></div>
            
            <div class="summary-line"><span>Subtotal:</span><span>$269.98</span></div>
            <div class="summary-line"><span>Shipping:</span><span style="color:#10B981; font-weight:600;">FREE</span></div>
            <div class="summary-line"><span>Estimated Tax:</span><span>$21.60</span></div>
            <div class="summary-line total"><span>Total Amount:</span><span>$291.58</span></div>
        </div>
    </div>
</div>
</body>
</html>
""",

    "T08": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
""" + SHARED_CSS + """
.navbar {
    height: 80px;
    padding: 0 80px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: transparent;
}
.brand {
    font-size: 24px;
    font-weight: 800;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 10px;
}
.brand-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #0B57D0;
}
.nav-links {
    display: flex;
    gap: 32px;
    list-style: none;
}
.nav-links a {
    color: #475569;
    text-decoration: none;
    font-size: 14.5px;
    font-weight: 600;
}
.nav-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}
.btn-login {
    background: none;
    border: none;
    font-size: 14px;
    font-weight: 600;
    color: #334155;
    cursor: pointer;
}
.btn-primary {
    background: #0B57D0;
    color: white;
    padding: 10px 22px;
    border-radius: 9999px;
    border: none;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(11, 87, 208, 0.25);
}
.hero {
    padding: 50px 80px 40px 80px;
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 50px;
    align-items: center;
}
.badge-pill {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #1D4ED8;
    font-size: 12.5px;
    font-weight: 700;
    padding: 6px 16px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
}
h1 {
    font-size: 46px;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -1.2px;
    color: #0F172A;
    margin-bottom: 18px;
}
h1 span {
    color: #0B57D0;
    background: linear-gradient(135deg, #0B57D0 0%, #2563EB 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
p.hero-desc {
    font-size: 16px;
    color: #64748B;
    line-height: 1.6;
    margin-bottom: 32px;
    max-width: 540px;
}
.cta-group {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 44px;
}
.btn-cta-main {
    background: #0B57D0;
    color: white;
    padding: 14px 30px;
    border-radius: 12px;
    border: none;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 8px 20px rgba(11, 87, 208, 0.3);
}
.btn-cta-secondary {
    background: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    padding: 14px 24px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
}
.social-proof {
    display: flex;
    align-items: center;
    gap: 20px;
}
.proof-item {
    font-size: 12.5px;
    color: #64748B;
    font-weight: 600;
}
.mockup-card {
    background: #FFFFFF;
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08);
    overflow: hidden;
}
.mockup-topbar {
    height: 38px;
    background: #F1F5F9;
    border-bottom: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 8px;
}
.mockup-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.mockup-content {
    padding: 24px;
    background: #FAFAFA;
}
.mockup-kpi {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
}
.mockup-chart-bar {
    height: 120px;
    background: linear-gradient(180deg, rgba(11,87,208,0.15) 0%, rgba(11,87,208,0.02) 100%);
    border-radius: 8px;
    border-bottom: 2px solid #0B57D0;
    display: flex;
    align-items: flex-end;
    padding: 10px;
    gap: 12px;
}
</style>
</head>
<body>
<div class="navbar">
    <div class="brand"><div class="brand-dot"></div>Nexus<span>AI</span></div>
    <ul class="nav-links">
        <li><a href="#">Products</a></li>
        <li><a href="#">Benchmark Suite</a></li>
        <li><a href="#">Research Papers</a></li>
        <li><a href="#">Documentation</a></li>
    </ul>
    <div class="nav-actions">
        <button class="btn-login">Sign In</button>
        <button class="btn-primary">Get Started Free</button>
    </div>
</div>

<div class="hero">
    <div>
        <div class="badge-pill">🚀 WebGenBench 2026 Scientific Suite</div>
        <h1>Next-Gen AI Automated <span>UI Synthesis</span></h1>
        <p class="hero-desc">Benchmark autonomous AI coding agents against production design criteria. Measure HTML validity, responsive geometry, accessibility, and visual fidelity in seconds.</p>
        
        <div class="cta-group">
            <button class="btn-cta-main">Start Free Benchmark</button>
            <button class="btn-cta-secondary">▶ Watch 2-min Demo</button>
        </div>

        <div class="social-proof">
            <span class="proof-item">✓ 144 Runs Evaluated</span>
            <span class="proof-item">✓ 6 Metric Engines</span>
            <span class="proof-item">✓ Fleiss' Kappa Validated</span>
        </div>
    </div>

    <div>
        <div class="mockup-card">
            <div class="mockup-topbar">
                <div class="mockup-dot" style="background:#EF4444;"></div>
                <div class="mockup-dot" style="background:#F59E0B;"></div>
                <div class="mockup-dot" style="background:#10B981;"></div>
            </div>
            <div class="mockup-content">
                <div class="mockup-kpi">
                    <div style="font-size:12px; color:#64748B; font-weight:600;">EVALUATION SCORE</div>
                    <div style="font-size:28px; font-weight:800; color:#0B57D0;">96.8 / 100</div>
                </div>
                <div class="mockup-chart-bar">
                    <div style="height:40%; width:16%; background:#93C5FD; border-radius:4px 4px 0 0;"></div>
                    <div style="height:70%; width:16%; background:#60A5FA; border-radius:4px 4px 0 0;"></div>
                    <div style="height:55%; width:16%; background:#3B82F6; border-radius:4px 4px 0 0;"></div>
                    <div style="height:90%; width:16%; background:#0B57D0; border-radius:4px 4px 0 0;"></div>
                    <div style="height:65%; width:16%; background:#1D4ED8; border-radius:4px 4px 0 0;"></div>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""
}

def generate_all_designs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        for task_id, html_content in TEMPLATES.items():
            # Render directly from in-memory HTML without creating temp files on disk
            page.set_content(html_content, wait_until="load")
            page.wait_for_timeout(300)

            out_png = DESIGNS_DIR / f"{task_id}_reference.png"
            page.screenshot(path=str(out_png))
            print(f"[OK] Generated Ground Truth: {out_png} (1440x900)")

            # Also copy to artifacts directory for immediate user viewing
            artifact_png = Path(f"C:/Users/jimmy/.gemini/antigravity/brain/c0cfbd33-cafc-4871-9c26-44df1a642285/{task_id}_reference.png")
            page.screenshot(path=str(artifact_png))

        browser.close()
    print("All 8 Reference Designs generated successfully without any HTML template files on disk!")

if __name__ == "__main__":
    generate_all_designs()
