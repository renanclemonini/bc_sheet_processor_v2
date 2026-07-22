# Botconversa Design System — Tokens

> White Mode · Contraste Claro · Hierarquia com diferença de 2 pesos

---

## 1. Paleta de Cores

### Brand

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-brand-blue-400` | `#6A96DA` | Blob decorativo, hover states |
| `--color-brand-blue-500` | `#4A7BC8` | Primário (botões, links, CTAs) |
| `--color-brand-blue-600` | `#3B65B0` | Primário hover |
| `--color-brand-blue-700` | `#2D4F8C` | Primário active / pressed |
| `--color-brand-green-300` | `#87CC79` | Blob decorativo, badge success |
| `--color-brand-green-500` | `#52A347` | Secundário / WhatsApp accent |
| `--color-brand-green-600` | `#3E8A35` | Secundário hover |

### Escala Azul (Primary)

| Token | Hex |
|-------|-----|
| `--color-blue-50` | `#EEF3FB` |
| `--color-blue-100` | `#D5E3F5` |
| `--color-blue-200` | `#AECAEC` |
| `--color-blue-300` | `#87B0E3` |
| `--color-blue-400` | `#6A96DA` |
| `--color-blue-500` | `#4A7BC8` |
| `--color-blue-600` | `#3B65B0` |
| `--color-blue-700` | `#2D4F8C` |
| `--color-blue-800` | `#1F3868` |
| `--color-blue-900` | `#112244` |

### Escala Verde (Secondary)

| Token | Hex |
|-------|-----|
| `--color-green-50` | `#EEF8ED` |
| `--color-green-100` | `#D5EED4` |
| `--color-green-200` | `#ACDC9A` |
| `--color-green-300` | `#87CC79` |
| `--color-green-400` | `#6CB860` |
| `--color-green-500` | `#52A347` |
| `--color-green-600` | `#3E8A35` |
| `--color-green-700` | `#2D6E26` |
| `--color-green-800` | `#1D5218` |
| `--color-green-900` | `#0E370B` |

### Neutros

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-neutral-0` | `#FFFFFF` | Background principal |
| `--color-neutral-50` | `#F8FAFC` | Surface / cards |
| `--color-neutral-100` | `#F1F5F9` | Input background |
| `--color-neutral-200` | `#E2E8F0` | Dividers / borders |
| `--color-neutral-300` | `#CBD5E1` | Borders hover |
| `--color-neutral-400` | `#94A3B8` | Placeholder text |
| `--color-neutral-500` | `#64748B` | Text muted |
| `--color-neutral-600` | `#475569` | Text secondary |
| `--color-neutral-700` | `#334155` | Text primary light |
| `--color-neutral-800` | `#1E293B` | Text primary |
| `--color-neutral-900` | `#0F172A` | Text heading |

### Semânticas

| Token | Valor | Uso |
|-------|-------|-----|
| `--color-success` | `#22C55E` | Confirmações, status ativo |
| `--color-success-bg` | `#F0FDF4` | Background success |
| `--color-warning` | `#F59E0B` | Alertas |
| `--color-warning-bg` | `#FFFBEB` | Background warning |
| `--color-error` | `#EF4444` | Erros, destrutivo |
| `--color-error-bg` | `#FEF2F2` | Background error |
| `--color-info` | `#3B82F6` | Informativo |
| `--color-info-bg` | `#EFF6FF` | Background info |

---

## 2. Tipografia

### Família

| Token | Valor |
|-------|-------|
| `--font-family-base` | `'Nunito Sans', system-ui, -apple-system, sans-serif` |
| `--font-family-mono` | `'JetBrains Mono', 'Fira Code', monospace` |

### Escala de Pesos
> Regra: diferença mínima de **2 pesos** (200 pontos) entre níveis hierárquicos

| Token | Valor | Nome |
|-------|-------|------|
| `--font-weight-regular` | `400` | Regular |
| `--font-weight-medium` | `500` | Medium |
| `--font-weight-semibold` | `600` | Semibold |
| `--font-weight-bold` | `700` | Bold |
| `--font-weight-extrabold` | `800` | Extrabold |

### Hierarquia (aplicação dos pesos)

| Nível | Peso Token | Peso | Relação |
|-------|-----------|------|---------|
| Display / Hero | `--font-weight-extrabold` | `800` | — |
| H1 | `--font-weight-bold` | `700` | ↓ 100 do display |
| H2 | `--font-weight-bold` | `700` | = H1 (mesmo nível) |
| H3 | `--font-weight-medium` | `500` | ↓ **200** do H1/H2 ✓ |
| H4 | `--font-weight-medium` | `500` | = H3 |
| Subtítulo / Label | `--font-weight-medium` | `500` | ↓ **200** do H1 ✓ |
| Body | `--font-weight-regular` | `400` | ↓ **100** do medium |
| Caption | `--font-weight-regular` | `400` | = body |
| Eyebrow (tag acima do título) | `--font-weight-semibold` | `600` | Entre H1 e H3 |

### Tamanhos

| Token | rem | px | Uso |
|-------|-----|----|-----|
| `--text-xs` | `0.75rem` | 12px | Caption, legenda |
| `--text-sm` | `0.875rem` | 14px | Helper text, badge |
| `--text-base` | `1rem` | 16px | Body padrão |
| `--text-lg` | `1.125rem` | 18px | Body large |
| `--text-xl` | `1.25rem` | 20px | H4 / Lead text |
| `--text-2xl` | `1.5rem` | 24px | H3 |
| `--text-3xl` | `1.875rem` | 30px | H2 mobile |
| `--text-4xl` | `2.25rem` | 36px | H2 desktop |
| `--text-5xl` | `3rem` | 48px | H1 desktop |
| `--text-6xl` | `3.75rem` | 60px | Display / Hero |
| `--text-7xl` | `4.5rem` | 72px | Hero XL |

### Line Height

| Token | Valor | Uso |
|-------|-------|-----|
| `--leading-none` | `1` | Títulos muito grandes |
| `--leading-tight` | `1.2` | Headings |
| `--leading-snug` | `1.35` | Subtítulos |
| `--leading-normal` | `1.5` | Body text |
| `--leading-relaxed` | `1.65` | Body long-form |

### Letter Spacing

| Token | Valor | Uso |
|-------|-------|-----|
| `--tracking-tighter` | `-0.05em` | Display / hero grandes |
| `--tracking-tight` | `-0.025em` | H1 |
| `--tracking-normal` | `0em` | Body |
| `--tracking-wide` | `0.05em` | Eyebrow / label uppercase |
| `--tracking-widest` | `0.1em` | Badge uppercase |

---

## 3. Espaçamento

> Base: 4px (0.25rem)

| Token | rem | px |
|-------|-----|----|
| `--space-1` | `0.25rem` | 4px |
| `--space-2` | `0.5rem` | 8px |
| `--space-3` | `0.75rem` | 12px |
| `--space-4` | `1rem` | 16px |
| `--space-5` | `1.25rem` | 20px |
| `--space-6` | `1.5rem` | 24px |
| `--space-8` | `2rem` | 32px |
| `--space-10` | `2.5rem` | 40px |
| `--space-12` | `3rem` | 48px |
| `--space-16` | `4rem` | 64px |
| `--space-20` | `5rem` | 80px |
| `--space-24` | `6rem` | 96px |
| `--space-32` | `8rem` | 128px |

---

## 4. Border Radius

| Token | Valor | Uso |
|-------|-------|-----|
| `--radius-sm` | `4px` | Tags, badges internos |
| `--radius-md` | `8px` | Inputs, botões small |
| `--radius-lg` | `12px` | Botões padrão, cards small |
| `--radius-xl` | `16px` | Cards, modais |
| `--radius-2xl` | `24px` | Cards hero, feature sections |
| `--radius-3xl` | `32px` | Cards ilustrativos grandes |
| `--radius-full` | `9999px` | Pills, badges, avatares |

---

## 5. Sombras

| Token | Valor | Uso |
|-------|-------|-----|
| `--shadow-xs` | `0 1px 2px rgba(15, 23, 42, 0.05)` | Hover sutil |
| `--shadow-sm` | `0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04)` | Cards default |
| `--shadow-md` | `0 4px 6px rgba(15, 23, 42, 0.07), 0 2px 4px rgba(15, 23, 42, 0.05)` | Cards hover |
| `--shadow-lg` | `0 10px 15px rgba(15, 23, 42, 0.08), 0 4px 6px rgba(15, 23, 42, 0.04)` | Dropdowns, popovers |
| `--shadow-xl` | `0 20px 25px rgba(15, 23, 42, 0.08), 0 8px 10px rgba(15, 23, 42, 0.04)` | Modais |
| `--shadow-2xl` | `0 25px 50px rgba(15, 23, 42, 0.12)` | Modais grandes |
| `--shadow-blue` | `0 8px 24px rgba(74, 123, 200, 0.25)` | Botão primário hover |
| `--shadow-green` | `0 8px 24px rgba(82, 163, 71, 0.25)` | CTA secundário hover |

---

## 6. Gradientes e Efeitos de Fundo

### Aurora Background (assinatura visual da marca)

```css
/* Fundo base da página */
--bg-page: #FFFFFF;

/* Blob 1 — canto superior direito */
--gradient-blob-blue: radial-gradient(ellipse at 85% 10%, rgba(106, 150, 218, 0.45) 0%, transparent 60%);

/* Blob 2 — canto inferior esquerdo */
--gradient-blob-green: radial-gradient(ellipse at 10% 85%, rgba(135, 204, 121, 0.40) 0%, transparent 55%);

/* Blob 3 — canto superior esquerdo (verde mais suave) */
--gradient-blob-green-top: radial-gradient(ellipse at 5% 5%, rgba(135, 204, 121, 0.25) 0%, transparent 45%);

/* Grain overlay (textura sobre o fundo) */
--grain-opacity: 0.035;
```

### Como aplicar o Aurora Background

```css
.page-background {
  background-color: #FFFFFF;
  background-image:
    radial-gradient(ellipse at 85% 10%, rgba(106, 150, 218, 0.45) 0%, transparent 60%),
    radial-gradient(ellipse at 10% 85%, rgba(135, 204, 121, 0.40) 0%, transparent 55%),
    radial-gradient(ellipse at 5% 5%, rgba(135, 204, 121, 0.25) 0%, transparent 45%),
    url("data:image/svg+xml,..."); /* grain via SVG noise filter */
  background-attachment: fixed;
}
```

### Gradientes de Componentes

| Token | Valor | Uso |
|-------|-------|-----|
| `--gradient-primary` | `linear-gradient(135deg, #4A7BC8 0%, #6A96DA 100%)` | Botão primário |
| `--gradient-hero` | `linear-gradient(135deg, #3B65B0 0%, #4A7BC8 50%, #6A96DA 100%)` | Hero sections |
| `--gradient-card-highlight` | `linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%)` | Cards elevados |
| `--gradient-brand-subtle` | `linear-gradient(135deg, rgba(74,123,200,0.08) 0%, rgba(135,204,121,0.06) 100%)` | Seções de destaque |

---

## 7. Cores Semânticas de Interface

### Texto

| Token | Hex | Uso |
|-------|-----|-----|
| `--text-heading` | `#0F172A` | Títulos H1–H3 |
| `--text-primary` | `#1E293B` | Body principal |
| `--text-secondary` | `#475569` | Subtítulos, descrições |
| `--text-muted` | `#64748B` | Placeholders, captions |
| `--text-disabled` | `#94A3B8` | Estados desabilitados |
| `--text-inverse` | `#FFFFFF` | Texto em fundo escuro |
| `--text-brand` | `#4A7BC8` | Links, destaques |
| `--text-brand-green` | `#3E8A35` | Destaques secundários |

### Background de Interface

| Token | Hex | Uso |
|-------|-----|-----|
| `--bg-page` | `#FFFFFF` | Página principal |
| `--bg-surface` | `#F8FAFC` | Cards, painéis |
| `--bg-surface-raised` | `#FFFFFF` | Cards elevados (com shadow) |
| `--bg-input` | `#F1F5F9` | Input fields |
| `--bg-overlay` | `rgba(15, 23, 42, 0.5)` | Modal backdrop |

### Bordas

| Token | Hex | Uso |
|-------|-----|-----|
| `--border-default` | `#E2E8F0` | Bordas padrão |
| `--border-strong` | `#CBD5E1` | Bordas em hover |
| `--border-brand` | `#4A7BC8` | Input focus, seleção |

---

## 8. Componentes — Tokens Aplicados

### Botão Primário

```
background:  --gradient-primary
color:       --text-inverse
font-size:   --text-base (16px)
font-weight: --font-weight-semibold (600)
padding:     --space-3 --space-6  (12px 24px)
border-radius: --radius-lg (12px)
shadow:      --shadow-blue (hover)
```

### Botão Secundário (Outline)

```
background:  transparent
border:      1.5px solid --color-blue-500
color:       --color-blue-500
font-size:   --text-base
font-weight: --font-weight-semibold (600)
padding:     --space-3 --space-6
border-radius: --radius-lg
```

### Botão Ghost

```
background:  transparent
color:       --color-blue-500
font-weight: --font-weight-medium (500)
border-radius: --radius-lg
```

### Card

```
background:    --bg-surface-raised (#FFFFFF)
border:        1px solid --border-default
border-radius: --radius-xl (16px)
shadow:        --shadow-sm (default) → --shadow-md (hover)
padding:       --space-6 (24px)
```

### Badge / Tag

```
font-size:     --text-xs (12px)
font-weight:   --font-weight-semibold (600)
letter-spacing: --tracking-wide
border-radius: --radius-full
padding:       --space-1 --space-3  (4px 12px)
```

### Input

```
background:    --bg-input (#F1F5F9)
border:        1px solid --border-default
border-radius: --radius-md (8px)
font-size:     --text-base
color:         --text-primary
padding:       --space-3 --space-4 (12px 16px)
focus border:  --border-brand
focus shadow:  0 0 0 3px rgba(74, 123, 200, 0.15)
```

---

## 9. Hierarquia Tipográfica — Exemplos de Uso

```
Display / Hero
  font-size:   60–72px (--text-6xl / --text-7xl)
  font-weight: 800 (--font-weight-extrabold)
  color:       --text-heading
  line-height: --leading-tight (1.2)
  letter-spacing: --tracking-tighter

H1
  font-size:   48px (--text-5xl)
  font-weight: 700 (--font-weight-bold)
  color:       --text-heading
  line-height: --leading-tight

H2
  font-size:   36px (--text-4xl)
  font-weight: 700 (--font-weight-bold)
  color:       --text-heading
  line-height: --leading-snug (1.35)

H3   ← diferença de 200 do H1/H2
  font-size:   24px (--text-2xl)
  font-weight: 500 (--font-weight-medium)
  color:       --text-primary
  line-height: --leading-snug

H4
  font-size:   20px (--text-xl)
  font-weight: 500 (--font-weight-medium)
  color:       --text-primary

Body Large
  font-size:   18px (--text-lg)
  font-weight: 400 (--font-weight-regular)
  color:       --text-secondary
  line-height: --leading-relaxed (1.65)

Body
  font-size:   16px (--text-base)
  font-weight: 400 (--font-weight-regular)
  color:       --text-secondary
  line-height: --leading-normal (1.5)

Caption / Helper
  font-size:   12–14px (--text-xs / --text-sm)
  font-weight: 400 (--font-weight-regular)
  color:       --text-muted

Eyebrow (label acima do título)
  font-size:   12px (--text-xs)
  font-weight: 600 (--font-weight-semibold)
  color:       --text-brand
  letter-spacing: --tracking-widest
  text-transform: uppercase
```

---

## 10. Grid e Layout

| Token | Valor |
|-------|-------|
| `--container-sm` | `640px` |
| `--container-md` | `768px` |
| `--container-lg` | `1024px` |
| `--container-xl` | `1280px` |
| `--container-2xl` | `1440px` |
| `--container-padding` | `24px (mobile) / 48px (desktop)` |
| `--grid-columns` | `12` |
| `--grid-gutter` | `24px` |

---

## 11. Motion / Animação

| Token | Valor | Uso |
|-------|-------|-----|
| `--duration-fast` | `100ms` | Micro-interações |
| `--duration-base` | `200ms` | Hovers, fades |
| `--duration-slow` | `350ms` | Modais, panels |
| `--duration-xslow` | `600ms` | Animações de entrada |
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Padrão suave |
| `--ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Saída de elementos |
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Entrada de elementos |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Botões, microanimações |

---

## 12. Z-Index

| Token | Valor | Uso |
|-------|-------|-----|
| `--z-below` | `-1` | Backgrounds decorativos |
| `--z-base` | `0` | Conteúdo padrão |
| `--z-raised` | `10` | Cards hover |
| `--z-dropdown` | `100` | Dropdowns |
| `--z-sticky` | `200` | Navbar sticky |
| `--z-overlay` | `300` | Overlay backdrop |
| `--z-modal` | `400` | Modais |
| `--z-toast` | `500` | Notificações |
| `--z-tooltip` | `600` | Tooltips |

---

## Referências Visuais

- **Fundo**: Aurora com grain — blobs suaves em `#6A96DA` (azul) e `#87CC79` (verde) sobre branco `#FFFFFF`
- **Textura**: Grain noise com opacidade ~3.5% sobre os gradientes
- **Estilo**: SaaS moderno, clean, light — sem sombras pesadas, sem escuros dominantes
- **Contraste**: Textos escuros (`#0F172A`) sobre brancos e superfícies claras para máxima legibilidade
