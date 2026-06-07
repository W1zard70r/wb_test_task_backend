import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BadgeRussianRuble,
  Box,
  Check,
  ChevronRight,
  LogOut,
  Minus,
  PackageCheck,
  Plus,
  Search,
  ShoppingBag,
  ShoppingCart,
  Sparkles,
  Trash2,
  UserRound,
  Wallet,
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "";
const TOKEN_KEY = "berry_market_tokens";

function money(value) {
  return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB" }).format(Number(value || 0));
}

function readTokens() {
  try {
    return JSON.parse(localStorage.getItem(TOKEN_KEY)) || null;
  } catch {
    return null;
  }
}

async function api(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const message = data?.detail || Object.values(data || {})?.flat?.()?.[0] || "Request failed";
    throw new Error(message);
  }
  return data;
}

function App() {
  const [tokens, setTokens] = useState(readTokens);
  const [me, setMe] = useState(null);
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({ items: [], total_price: "0.00" });
  const [orders, setOrders] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [query, setQuery] = useState("");
  const [authMode, setAuthMode] = useState("login");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const token = tokens?.access;

  const selectedItems = useMemo(
    () => cart.items.filter((item) => selectedIds.has(item.id)),
    [cart.items, selectedIds],
  );
  const selectedTotal = selectedItems.reduce((sum, item) => sum + Number(item.total_price), 0);

  async function run(action, successMessage) {
    setError("");
    setNotice("");
    try {
      const result = await action();
      if (successMessage) setNotice(successMessage);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }

  async function loadPublicProducts(search = query) {
    const params = new URLSearchParams({ in_stock: "true" });
    if (search.trim()) params.set("search", search.trim());
    const data = await api(`/api/products/?${params.toString()}`);
    setProducts(data.results || []);
  }

  async function loadPrivateData() {
    if (!token) return;
    const [profile, cartData, ordersData] = await Promise.all([
      api("/api/auth/me/", { token }),
      api("/api/cart/", { token }),
      api("/api/orders/", { token }),
    ]);
    setMe(profile);
    setCart(cartData);
    setOrders(ordersData.results || ordersData || []);
    setSelectedIds((current) => {
      const available = new Set(cartData.items.map((item) => item.id));
      return new Set([...current].filter((id) => available.has(id)));
    });
  }

  useEffect(() => {
    loadPublicProducts().catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (token) loadPrivateData().catch((err) => setError(err.message));
    if (!token) {
      setMe(null);
      setCart({ items: [], total_price: "0.00" });
      setOrders([]);
      setSelectedIds(new Set());
    }
  }, [token]);

  async function login(form) {
    const data = await run(
      () => api("/api/auth/token/", { method: "POST", body: form }),
      "Готово, ты вошел в аккаунт",
    );
    localStorage.setItem(TOKEN_KEY, JSON.stringify(data));
    setTokens(data);
  }

  async function register(form) {
    await run(() => api("/api/auth/register/", { method: "POST", body: form }), "Аккаунт создан");
    await login({ username: form.username, password: form.password });
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setTokens(null);
    setNotice("Ты вышел из аккаунта");
  }

  async function addToCart(product) {
    if (!token) {
      setError("Сначала войди или зарегистрируйся");
      return;
    }
    await run(
      () => api("/api/cart/items/", { method: "POST", token, body: { product_id: product.id, quantity: 1 } }),
      "Товар добавлен в корзину",
    );
    await loadPrivateData();
  }

  async function updateQuantity(item, delta) {
    const next = item.quantity + delta;
    if (next < 1) return;
    await run(() => api(`/api/cart/items/${item.id}/`, { method: "PATCH", token, body: { quantity: next } }));
    await loadPrivateData();
  }

  async function removeItem(item) {
    await run(() => api(`/api/cart/items/${item.id}/`, { method: "DELETE", token }), "Позиция удалена");
    await loadPrivateData();
  }

  async function topUp(amount) {
    await run(
      () => api("/api/auth/me/balance/top-up/", { method: "POST", token, body: { amount } }),
      "Баланс пополнен",
    );
    await loadPrivateData();
  }

  async function checkoutSelected() {
    if (!selectedIds.size) {
      setError("Выбери товары для оплаты");
      return;
    }
    await run(
      () => api("/api/orders/", { method: "POST", token, body: { cart_item_ids: [...selectedIds] } }),
      "Заказ оплачен, выбранные товары ушли в историю",
    );
    await Promise.all([loadPrivateData(), loadPublicProducts()]);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><ShoppingBag size={24} /></div>
          <div>
            <strong>Berry Market</strong>
            <span>маркетплейс</span>
          </div>
        </div>
        <form className="search" onSubmit={(event) => { event.preventDefault(); run(() => loadPublicProducts()); }}>
          <Search size={18} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Найти товары" />
        </form>
        <div className="top-actions">
          {me ? (
            <>
              <div className="pill"><Wallet size={17} />{money(me.balance)}</div>
              <button className="ghost-button" onClick={logout} title="Выйти"><LogOut size={18} /></button>
            </>
          ) : (
            <div className="pill"><UserRound size={17} />Гость</div>
          )}
        </div>
      </header>

      {(notice || error) && (
        <div className={`toast ${error ? "toast-error" : ""}`}>{error || notice}</div>
      )}

      <main className="layout">
        <section className="catalog-panel">
          <div className="section-head">
            <div>
              <h1>Витрина</h1>
              <p>Добавляй товары в корзину и оплачивай только выбранные позиции.</p>
            </div>
            <div className="stat"><Sparkles size={17} />{products.length} товаров</div>
          </div>
          <div className="product-grid">
            {products.map((product) => (
              <article className="product-card" key={product.id}>
                <div className="product-art"><Box size={42} /></div>
                <div className="product-body">
                  <h3>{product.title}</h3>
                  <p>{product.description || "Новый товар с быстрой доставкой"}</p>
                  <div className="product-meta">
                    <strong>{money(product.price)}</strong>
                    <span>{product.stock_quantity} шт.</span>
                  </div>
                  <button className="primary-button" onClick={() => addToCart(product)}>
                    <ShoppingCart size={18} />В корзину
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>

        <aside className="side-panel">
          {!me ? (
            <AuthPanel mode={authMode} setMode={setAuthMode} onLogin={login} onRegister={register} />
          ) : (
            <>
              <AccountPanel me={me} onTopUp={topUp} />
              <CartPanel
                cart={cart}
                selectedIds={selectedIds}
                setSelectedIds={setSelectedIds}
                selectedTotal={selectedTotal}
                onQuantity={updateQuantity}
                onRemove={removeItem}
                onCheckout={checkoutSelected}
              />
              <OrdersPanel orders={orders} />
            </>
          )}
        </aside>
      </main>
    </div>
  );
}

function AuthPanel({ mode, setMode, onLogin, onRegister }) {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const isLogin = mode === "login";
  return (
    <section className="auth-panel compact-panel">
      <h2>{isLogin ? "Вход" : "Регистрация"}</h2>
      <label>Логин<input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
      {!isLogin && <label>Email<input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>}
      <label>Пароль<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
      <button className="primary-button wide" onClick={() => isLogin ? onLogin(form) : onRegister(form)}>
        <UserRound size={18} />{isLogin ? "Войти" : "Создать аккаунт"}
      </button>
      <button className="text-button" onClick={() => setMode(isLogin ? "register" : "login")}>
        {isLogin ? "Создать новый аккаунт" : "Уже есть аккаунт"}<ChevronRight size={16} />
      </button>
    </section>
  );
}

function AccountPanel({ me, onTopUp }) {
  const [amount, setAmount] = useState("1000.00");
  return (
    <section className="compact-panel account-panel">
      <div className="panel-title"><Wallet size={19} /><h2>Баланс</h2></div>
      <div className="balance-value">{money(me.balance)}</div>
      <div className="inline-form">
        <input value={amount} onChange={(event) => setAmount(event.target.value)} />
        <button className="icon-button" onClick={() => onTopUp(amount)} title="Пополнить"><Plus size={18} /></button>
      </div>
    </section>
  );
}

function CartPanel({ cart, selectedIds, setSelectedIds, selectedTotal, onQuantity, onRemove, onCheckout }) {
  const allSelected = cart.items.length > 0 && cart.items.every((item) => selectedIds.has(item.id));
  function toggle(id) {
    setSelectedIds((current) => {
      const next = new Set(current);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }
  function toggleAll() {
    setSelectedIds(allSelected ? new Set() : new Set(cart.items.map((item) => item.id)));
  }
  return (
    <section className="compact-panel cart-panel">
      <div className="panel-title"><ShoppingCart size={19} /><h2>Корзина</h2></div>
      <button className="select-all" onClick={toggleAll}><Check size={16} />{allSelected ? "Снять выбор" : "Выбрать все"}</button>
      <div className="cart-list">
        {cart.items.map((item) => (
          <div className="cart-row" key={item.id}>
            <button className={`check ${selectedIds.has(item.id) ? "checked" : ""}`} onClick={() => toggle(item.id)} title="Выбрать товар">
              {selectedIds.has(item.id) && <Check size={14} />}
            </button>
            <div className="cart-info">
              <strong>{item.product.title}</strong>
              <span>{money(item.total_price)}</span>
            </div>
            <div className="stepper">
              <button onClick={() => onQuantity(item, -1)} title="Уменьшить"><Minus size={14} /></button>
              <b>{item.quantity}</b>
              <button onClick={() => onQuantity(item, 1)} title="Увеличить"><Plus size={14} /></button>
            </div>
            <button className="trash" onClick={() => onRemove(item)} title="Удалить"><Trash2 size={16} /></button>
          </div>
        ))}
        {!cart.items.length && <p className="empty">Корзина пока пустая</p>}
      </div>
      <div className="checkout-box">
        <div><span>К оплате</span><strong>{money(selectedTotal)}</strong></div>
        <button className="primary-button wide" onClick={onCheckout}><BadgeRussianRuble size={18} />Оплатить выбранное</button>
      </div>
    </section>
  );
}

function OrdersPanel({ orders }) {
  return (
    <section className="compact-panel orders-panel">
      <div className="panel-title"><PackageCheck size={19} /><h2>Заказы</h2></div>
      <div className="orders-list">
        {orders.slice(0, 5).map((order) => (
          <div className="order-row" key={order.id}>
            <div><strong>#{order.id}</strong><span>{order.items.length} поз.</span></div>
            <b>{money(order.total_amount)}</b>
          </div>
        ))}
        {!orders.length && <p className="empty">История заказов пустая</p>}
      </div>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
