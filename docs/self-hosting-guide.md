# 🖥️ Host ShopForge on Your Mac — A Complete Beginner's Guide

> **Goal:** Run ShopForge on your MacBook so that friends, family, or colleagues
> can open your website from *their* devices without you deploying to AWS, Heroku,
> or any paid cloud service.

---

## 📖 Table of Contents

1. [How the Internet Actually Works (the 2-minute version)](#1-how-the-internet-actually-works)
2. [What "Running a Server on Your Laptop" Really Means](#2-what-running-a-server-on-your-laptop-means)
3. [Step 0 — Prerequisites & What You Already Have](#3-step-0--prerequisites)
4. [Step 1 — Run ShopForge Locally (LAN access)](#4-step-1--run-shopforge-and-access-it-on-your-wi-fi-network)
5. [Step 2 — Share With the World Safely Using ngrok](#5-step-2--share-with-anyone-on-the-internet-using-ngrok)
6. [Step 3 — Keep It Running While You Close the Lid (optional)](#6-step-3--keeping-the-site-alive)
7. [Advanced: Port Forwarding (permanent, no ngrok)](#7-advanced-port-forwarding--static-ip)
8. [Safety Rules You Must Follow](#8-safety-rules)
9. [Limitations of a Laptop Server (be honest with yourself)](#9-limitations-of-a-laptop-server)
10. [Quick-Reference Cheat Sheet](#10-quick-reference-cheat-sheet)

---

## 1. How the Internet Actually Works

Think of the internet as a giant postal system.

```
  YOU (browser)                             SERVER (your Mac)
  ──────────────                            ─────────────────
  "I want shopforge.com/products"   ──▶     receives the request
                                    ◀──     sends back HTML/JSON
```

Every device on the internet has an **IP address** — like a home address for data.
There are two kinds:

| Kind | What it looks like | Who can reach it |
|------|-------------------|-----------------|
| **Private / Local IP** | `192.168.x.x` | Only devices on your same Wi-Fi |
| **Public IP** | `203.0.113.42` | Anyone on the internet |

Your Mac right now has **both**:
- A **private IP** given by your home router (e.g. `192.168.1.5`)
- A **public IP** shared by your entire home network (one IP for everyone)

A **port** is like the apartment number inside that address.
ShopForge uses **port 8000** for Django. So the full "address" of ShopForge
on your machine is: `192.168.1.5:8000`.

---

## 2. What "Running a Server on Your Laptop" Means

Normally a "server" is a computer in a data center that never sleeps. Your
MacBook can do the exact same job — it just has a few real-world limitations
(covered in §9). For learning, demos, and showing people your project, it is
**completely fine**.

Here is the big picture of what we will set up:

```
  Friend's phone/laptop
         │
         │  https://abc123.ngrok.io
         ▼
   [ngrok servers] ──── encrypted tunnel ───▶ [Your Mac :8000]
                                                      │
                                              [ShopForge Django]
                                              [Postgres + Redis]
                                              [Vue Frontend]
```

**ngrok** is a free tool that creates a secure, encrypted tunnel from the
internet to your laptop. Your Mac never needs a static public IP, you never
need to touch your router, and the connection is HTTPS by default. It is the
safest and easiest way to get started.

---

## 3. Step 0 — Prerequisites

### Things you already have ✅
- Docker Desktop (you used `make build` and `make run`)
- The ShopForge repo at `~/Downloads/STG_LOS/.../shopforge`
- A `.env` file with working local credentials

### Things you need to install

#### 1. Homebrew (if not already installed)
Open **Terminal** and run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Homebrew is macOS's package manager — think of it like an App Store for
developer tools.

#### 2. ngrok
```bash
brew install ngrok/ngrok/ngrok
```

#### 3. Create a free ngrok account
Go to [https://ngrok.com](https://ngrok.com), sign up for free (no credit card).

After signing up, ngrok gives you an **authtoken**. Copy it — it looks like:
`2abc123XYZ_someRandomString`.

Connect ngrok to your account:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```
You only need to do this once.

---

## 4. Step 1 — Run ShopForge and Access It on Your Wi-Fi Network

### 4a. Start ShopForge

Open Terminal, navigate to your repo, and start everything:

```bash
cd ~/Downloads/STG_LOS/corporate-django-ecommerce-tutorial/shopforge
make run
```

Wait about 30 seconds for all containers to start. You should see output from
Django, Celery, and Vite. When it settles, ShopForge is running at:

```
http://localhost:8000
```

Open your browser and confirm it loads. 🎉

### 4b. Find your Mac's local IP address

```bash
ipconfig getifaddr en0
```

This prints something like `192.168.1.42`. That is your Mac's address on the
local Wi-Fi. Write it down.

> **Tip:** If the command returns nothing, try `en1` instead (some Macs use
> `en1` for Wi-Fi). Or go to **System Settings → Network → Wi-Fi → Details**.

### 4c. Access ShopForge from another device on the same Wi-Fi

On your phone (connected to the **same Wi-Fi**), open the browser and type:

```
http://192.168.1.42:8000
```

(Replace with your actual IP from step 4b.)

If it loads — congratulations, your Mac is now a web server for your local
network! 🥳

> **If it does NOT load**, it's likely macOS firewall blocking the port. Fix:
> **System Settings → Privacy & Security → Firewall → Firewall Options** →
> make sure Docker is allowed, or temporarily disable the firewall for testing.

---

## 5. Step 2 — Share With Anyone on the Internet Using ngrok

This is where it gets exciting. With one command, you give ShopForge a real
internet address that anyone can visit.

### 5a. Make sure ShopForge is already running

```bash
make run   # if not already running
```

### 5b. Open a second Terminal tab and start ngrok

```bash
ngrok http 8000
```

You will see a dashboard like this in your terminal:

```
ngrok                                                    (Ctrl+C to quit)

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://a1b2c3d4.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

The key line is:

```
Forwarding   https://a1b2c3d4.ngrok-free.app -> http://localhost:8000
```

That `https://a1b2c3d4.ngrok-free.app` URL is your **live public website**.
Copy it and send it to anyone — they can open it on their laptop or phone from
anywhere in the world. 🌍

### 5c. Tell Django to trust the ngrok domain

Django has a security setting called `ALLOWED_HOSTS` that only accepts
requests from known domains. You need to add the ngrok domain.

Open a **third Terminal tab** (while `make run` and `ngrok` are still running):

```bash
cd ~/Downloads/STG_LOS/corporate-django-ecommerce-tutorial/shopforge
```

Open your `.env` file (or `config/settings/local.py`) and find `DJANGO_ALLOWED_HOSTS`.
Add the ngrok domain:

```
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,a1b2c3d4.ngrok-free.app
```

Then restart Django (Ctrl+C on `make run`, then `make run` again).

> **Free plan note:** ngrok's free plan gives you a **random subdomain** that
> changes every time you restart ngrok. Paid plans give you a **fixed subdomain**
> (e.g. `shopforge.ngrok.app`). For demos and testing, the random one is fine.

### 5d. Watch live traffic in the ngrok inspector

While ngrok is running, open your browser and go to:

```
http://127.0.0.1:4040
```

This is ngrok's built-in dashboard. You can see every request that comes in,
inspect headers, replay requests, and debug issues in real time. It's like a
superpower for understanding what your server receives. 🔍

---

## 6. Step 3 — Keeping the Site Alive

### The problem
When you close your MacBook lid, it sleeps. When it sleeps, Docker pauses.
Your website goes offline.

### Solution A — Prevent sleep while hosting
Go to **System Settings → Battery → Options** → set
"Prevent automatic sleeping on power adapter when the display is off" to ON.
Plug in your charger.

### Solution B — macOS "caffeinate" command
Run this in a Terminal tab to prevent sleep for 8 hours:

```bash
caffeinate -t 28800
```

Press Ctrl+C when you want normal sleep back.

### Solution C — Schedule start/stop
If you only want the site up during certain hours, you can use a startup
script. But for a beginner, Solutions A/B are plenty.

---

## 7. Advanced: Port Forwarding & Static IP

> ⚠️ **Skip this section if you are a beginner.** ngrok is safer and easier.
> Port forwarding opens your router to the internet, which requires care.

### What port forwarding is

Instead of using ngrok's tunnel, you configure your **home router** to
directly forward internet traffic on a specific port to your Mac. This means
anyone can reach your Mac using your home's **public IP address**.

### Step-by-step (general — every router is slightly different)

#### 1. Reserve a static local IP for your Mac

Open your router admin panel (usually `http://192.168.1.1` or
`http://192.168.0.1` in a browser). Find **DHCP Reservation** or
**Static IP Assignment** and assign your Mac's MAC address a fixed local IP
(e.g. always `192.168.1.42`). This prevents your Mac's local IP from changing.

#### 2. Set up port forwarding

In the router admin panel, find **Port Forwarding** (sometimes under
"NAT" or "Virtual Server"). Create a rule:

| Field | Value |
|-------|-------|
| Protocol | TCP |
| External Port | 8000 (or 80 for standard HTTP) |
| Internal IP | 192.168.1.42 (your Mac's static local IP) |
| Internal Port | 8000 |

#### 3. Find your public IP

```bash
curl ifconfig.me
```

This prints your public IP, e.g. `203.0.113.42`. Anyone can now reach your
site at `http://203.0.113.42:8000`.

#### 4. Deal with your changing public IP (Dynamic DNS)

Most home internet plans give you a **dynamic public IP** that changes
periodically. To get a stable hostname, use a free Dynamic DNS service:

- **[No-IP](https://www.noip.com)** — free, gives you `yourname.ddns.net`
- **[DuckDNS](https://www.duckdns.org)** — free, gives you `yourname.duckdns.org`

Install their small update client on your Mac. It automatically updates the
DNS record whenever your public IP changes. Now your site lives at a
stable address like `shopforge.ddns.net:8000`.

> **Why ngrok is better for beginners:** Port forwarding works but you are
> responsible for your own security. ngrok handles HTTPS, DDoS protection,
> and IP hiding automatically.

---

## 8. Safety Rules

Running a public server means the internet can see your machine. Follow these
rules to stay safe:

### ✅ DO

| Rule | Why |
|------|-----|
| Use ngrok (not raw port forwarding) for demos | ngrok hides your real IP and adds a layer of protection |
| Keep Docker and your OS updated | Security patches prevent known exploits |
| Use a **strong Django secret key** (already in your `.env`) | Prevents session forgery |
| Turn off ngrok when you are done | No tunnel = no attack surface |
| Never share your `.env` file | It contains your database password and secret key |
| Use `DEBUG=False` if real users will browse the site | Debug mode leaks sensitive info in error pages |

### ❌ DON'T

| Rule | Why |
|------|-----|
| Don't use `DEBUG=True` with a public URL | Shows full stack traces with internal file paths to anyone |
| Don't open port 22 (SSH) to the internet via port forwarding | Bots scan for this constantly |
| Don't use the default admin password | Change it immediately (`make sp` → `User.objects.get(is_superuser=True).set_password("new")` → `.save()`) |
| Don't store real credit card data | You don't have PCI compliance |
| Don't leave ngrok running overnight unattended | Check who is connecting via the inspector at `127.0.0.1:4040` |

### 🔐 Setting DEBUG=False for public sharing

Edit your `.env` file:

```
DJANGO_DEBUG=False
```

Then collect static files (so the site looks correct without Vite's dev server):

```bash
make bash
python manage.py collectstatic --noinput
exit
```

And restart: `make run`.

> For a quick internal demo with friends, `DEBUG=True` is fine. For anything
> you share publicly (e.g. in a portfolio), set it to False.

---

## 9. Limitations of a Laptop Server

Be honest about what a MacBook is and isn't:

| Thing | Cloud Server | Your MacBook |
|-------|-------------|-------------|
| Always online | ✅ 99.9% uptime | ❌ Offline when closed/sleeping |
| Fixed IP address | ✅ Usually static | ❌ Changes periodically |
| HTTPS certificate | ✅ Auto with services like Vercel | ⚠️ ngrok handles it; raw port forward needs manual setup |
| Can handle 1,000 concurrent users | ✅ With proper infra | ❌ Would likely overheat |
| Safe for real customer data | ✅ (with proper config) | ❌ Not production-ready |
| Great for demos & learning | ✅ | ✅ Perfect for this |

**Bottom line:** Your MacBook is perfect for demos, portfolio reviews, showing
a hiring manager, or learning. It is not a replacement for a proper hosting
service when real users depend on it.

---

## 10. Quick-Reference Cheat Sheet

```bash
# ── Start ShopForge ───────────────────────────────────────────────────
cd ~/Downloads/STG_LOS/corporate-django-ecommerce-tutorial/shopforge
make run

# ── Find your local IP (for LAN access) ──────────────────────────────
ipconfig getifaddr en0
# → e.g. 192.168.1.42
# Anyone on same Wi-Fi: open http://192.168.1.42:8000

# ── Start ngrok tunnel (internet access) ─────────────────────────────
ngrok http 8000
# → copy the https://xxxxx.ngrok-free.app URL

# ── Watch live traffic ────────────────────────────────────────────────
open http://127.0.0.1:4040

# ── Prevent Mac from sleeping ─────────────────────────────────────────
caffeinate -t 28800    # keeps awake for 8 hours

# ── Find your public IP ───────────────────────────────────────────────
curl ifconfig.me

# ── Stop everything ──────────────────────────────────────────────────
# Ctrl+C on ngrok terminal tab
make stop              # stops Docker containers
```

---

## 🗺️ The Full Flow in One Diagram

```
YOUR MAC
┌──────────────────────────────────────────────────────┐
│                                                      │
│  make run                                            │
│  ┌─────────────┐   ┌──────────┐   ┌──────────────┐  │
│  │  Django     │   │ Postgres │   │    Redis     │  │
│  │  :8000      │──▶│  :5432   │   │   :6379      │  │
│  └──────┬──────┘   └──────────┘   └──────────────┘  │
│         │                                            │
│  ngrok http 8000                                     │
│  ┌──────▼──────────────────────────────────────────┐ │
│  │  encrypted tunnel to ngrok servers               │ │
│  └──────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
         ▲
         │  https://abc123.ngrok-free.app
         │
   ┌─────┴──────┐    ┌──────────────┐    ┌───────────────┐
   │  ngrok     │    │ Your friend's│    │  Your phone   │
   │  servers   │◀───│  laptop      │    │  on 4G/5G     │
   └────────────┘    └──────────────┘    └───────────────┘
```

---

## ✅ Your Beginner Action Checklist

Work through these one by one:

- [ ] Run `make run` and confirm `http://localhost:8000` loads
- [ ] Run `ipconfig getifaddr en0` and note your local IP
- [ ] Open ShopForge from your phone on the same Wi-Fi
- [ ] Install ngrok: `brew install ngrok/ngrok/ngrok`
- [ ] Create a free account at [ngrok.com](https://ngrok.com) and add your authtoken
- [ ] Run `ngrok http 8000` and copy the public URL
- [ ] Add the ngrok domain to `DJANGO_ALLOWED_HOSTS` in your `.env`
- [ ] Restart `make run` and confirm the ngrok URL works from your phone on mobile data (not Wi-Fi!)
- [ ] Open `http://127.0.0.1:4040` and watch your own traffic
- [ ] Share the ngrok URL with a friend and watch their requests in the inspector

Once you have ticked all of these, you are officially running a live website
from your MacBook. 🚀

---

*Guide written for ShopForge — Django 5.2 + Vue 3 + Docker Compose on macOS.*
