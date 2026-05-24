//+------------------------------------------------------------------+
//|                                      ORB_MultiSymbol_v4.7.mq5    |
//|                         Opening Range Breakout - LDN & NY & ASN   |
//|          Multi-Asset (FX/Índices/Metales/Petróleo) | Dual TP      |
//+------------------------------------------------------------------+
#property copyright   "BlackSheep Quant Lab"
#property link        ""
#property version     "4.70"
#property description "ORB multi-activo: FX, Índices, Metales, Petróleo"
#property description "v4.7 — TP2=0 (runner sin TP fijo) + trailing auto-activo"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>

//+------------------------------------------------------------------+
//| ENUMS                                                             |
//+------------------------------------------------------------------+
enum ENUM_ORB_TIMEFRAME  { ORB_M15=0, ORB_M30=1, ORB_AMBOS=2 };
enum ENUM_SESSION_MODE   { SESION_NY=0, SESION_LDN=1, SESION_NY_LDN=2,
                           SESION_ASIA=3, SESION_ASIA_LDN=4, SESION_TODAS=5 };
enum ENUM_SYMBOL_PRESET  { PRESET_GRAFICO=0, PRESET_TODOS=1, PRESET_MAJORS=2, PRESET_CROSSES=3,
                           PRESET_JPY=4, PRESET_EUR=5, PRESET_GBP=6, PRESET_TOP5=7, PRESET_MANUAL=8,
                           PRESET_CSI=9,
                           PRESET_INDICES_EU=10, PRESET_INDICES_US=11, PRESET_INDICES_ALL=12,
                           PRESET_METALES=13, PRESET_ENERGIA=14, PRESET_MULTIASSET=15,
                           PRESET_CSI_MAJORS=16 };
enum ENUM_GMT_MODE       { GMT_AUTOMATICO=0, GMT_MANUAL=1 };
enum ENUM_ENTRY_MODE     { ENTRADA_MERCADO=0, ENTRADA_PULLBACK=1, ENTRADA_AMBAS=2 };
enum ENUM_FAKEOUT_MODE   { FAKEOUT_OFF=0, FAKEOUT_SOLO=1, FAKEOUT_Y_NORMAL=2 };
enum ENUM_DIR_FILTER     { DIR_AMBAS=0, DIR_SOLO_COMPRAS=1, DIR_SOLO_VENTAS=2 };
enum ENUM_ORB_MODE       { MODO_ORB=0, MODO_ANTI=1, MODO_AMBOS=2 };
enum ENUM_CSI_MODE       { CSI_FILTRO=0, CSI_ESTRICTO=1, CSI_SOLO_INFO=2 };
enum ENUM_ASSET_CLASS    { CLASS_FX=0, CLASS_INDEX=1, CLASS_METAL=2, CLASS_ENERGY=3, CLASS_UNKNOWN=4 };

//+------------------------------------------------------------------+
//| INPUTS                                                            |
//+------------------------------------------------------------------+
sinput string              _s0 = "════════ SÍMBOLOS ════════";
input  ENUM_SYMBOL_PRESET  InpPreset          = PRESET_GRAFICO;  // Qué símbolos va a vigilar el EA
input  string              InpCustom          = "";              // Solo si eliges lista manual, separados por comas

sinput string              _s1 = "════════ SESIÓN ════════";
input  ENUM_SESSION_MODE   InpSession         = SESION_NY;       // Sesión o combinación de sesiones a operar
sinput string              _s1a = "--- Nueva York (GMT) ---";
input  int                 InpNY_H            = 13;              // Hora de inicio de Nueva York en GMT
input  int                 InpNY_M            = 30;              // Minuto de inicio de Nueva York en GMT
input  int                 InpNY_End          = 20;              // Hora de fin de Nueva York en GMT
sinput string              _s1b = "--- Londres (GMT) ---";
input  int                 InpLDN_H           = 8;               // Hora de inicio de Londres en GMT
input  int                 InpLDN_M           = 0;               // Minuto de inicio de Londres en GMT
input  int                 InpLDN_End         = 12;              // Hora de fin de Londres en GMT
sinput string              _s1ba = "--- Asia (GMT) ---";
input  int                 InpASN_H           = 0;               // Hora de inicio de Asia en GMT
input  int                 InpASN_M           = 0;               // Minuto de inicio de Asia en GMT
input  int                 InpASN_End         = 6;               // Hora de fin de Asia en GMT
sinput string              _s1c = "--- Horario del bróker ---";
input  ENUM_GMT_MODE       InpGMT             = GMT_AUTOMATICO;  // Detectar GMT automáticamente o ponerlo manual
input  int                 InpGMTOff          = 2;               // Desfase horario del servidor del bróker respecto a GMT

sinput string              _s1d = "--- Días permitidos ---";
input  bool                InpMon             = true;            // Permite operar los lunes
input  bool                InpTue             = true;            // Permite operar los martes
input  bool                InpWed             = true;            // Permite operar los miércoles
input  bool                InpThu             = true;            // Permite operar los jueves
input  bool                InpFri             = true;            // Permite operar los viernes

sinput string              _s2 = "════════ RANGO ORB ════════";
input  ENUM_ORB_TIMEFRAME  InpTF              = ORB_AMBOS;       // Calcular ORB con 15m, 30m o ambos
input  double              InpMinPips         = 3.0;             // No operar si el rango inicial es demasiado pequeño
input  double              InpMaxPips         = 50.0;            // No operar si el rango inicial es demasiado grande

sinput string              _s2v = "════════ FILTRO VWAP ════════";
input  bool                InpVWAP            = true;            // Exigir alineación con VWAP para validar entradas
input  ENUM_TIMEFRAMES     InpVWAP_TF         = PERIOD_M15;      // Marco temporal usado para calcular el VWAP
input  int                 InpVWAP_Anchor     = 1;               // 0=diario, 1=apertura Londres, 2=apertura Asia
input  int                 InpVWAP_Days       = 3;               // Días históricos usados por el cálculo / dibujo del VWAP

sinput string              _s2c = "═══ FUERZA DE DIVISAS (CSI) ═══";
input  bool                InpCSI             = true;            // Activar filtro de fuerza de divisas + panel
input  ENUM_CSI_MODE       InpCSI_Mode        = CSI_FILTRO;      // Filtro=bloquea dir contraria | Estricto=solo mejor par | Info=solo muestra
input  int                 InpCSI_Lookback    = 10;              // Velas de cálculo para la fuerza
input  ENUM_TIMEFRAMES     InpCSI_TF          = PERIOD_H1;       // Marco temporal para calcular la fuerza
input  double              InpCSI_MinDiff     = 15.0;            // Diferencia mínima de fuerza para permitir trade (0-100)
input  int                 InpMaxPairs        = 2;               // Máximo de pares a operar por sesión (1-7)
input  double              InpCSI_MinConv     = 0.05;            // Spread mínimo real entre divisas para operar (% | 0=off)

sinput string              _s3 = "════════ OPERATIVA ════════";
sinput string              _s3m = "--- Modo ORB ---";
input  ENUM_ORB_MODE       InpMode            = MODO_ORB;        // ORB normal, Anti-ORB o ambas
input  ENUM_ENTRY_MODE     InpEntry           = ENTRADA_MERCADO;  // Entrar a mercado, en pullback o en ambos modos
input  double              InpPBOffset        = 0.5;             // Distancia en pips para colocar la limit de retroceso
sinput string              _s3f = "--- Modo fakeout ---";
input  ENUM_FAKEOUT_MODE   InpFakeout         = FAKEOUT_OFF;     // Ignorar fakeout, operar solo fakeout o ambos
sinput string              _s3d = "--- Dirección permitida ---";
input  ENUM_DIR_FILTER     InpDirection       = DIR_AMBAS;       // Comprar y vender, o limitar a una sola dirección
sinput string              _s3s = "--- Spread y objetivos ---";
input  double              InpMaxSpread       = 0;               // Spread máximo permitido en pips (0 = sin filtro)
input  double              InpTP1             = 10.0;            // Objetivo 1 en pips
input  double              InpTP2             = 30.0;            // Objetivo 2 en pips (0 = runner, sin TP fijo, trailing obligatorio)
input  bool                InpBE              = true;            // Pasar T2 a break even cuando T1 desaparece
input  double              InpBEOff           = 1.0;             // Pips extra al mover el stop a break even
sinput string              _s3t = "--- Trailing stop ---";
input  bool                InpTrail           = false;           // Activar trailing stop en la posición T2
input  double              InpTrailStep       = 10.0;            // Distancia en pips del trailing respecto al mejor precio
sinput string              _s3e = "--- Fin de sesión ---";
input  bool                InpCloseEOS        = false;           // Cerrar trades y pendientes al terminar la sesión

sinput string              _s4 = "════════ RIESGO ════════";
input  double              InpLot             = 0.02;            // Lote fijo
input  bool                InpRiskPct         = false;           // Calcular el lote por porcentaje de riesgo
input  double              InpRisk            = 1.0;             // Porcentaje a arriesgar por operación
input  int                 InpMaxPerDay       = 2;               // Máximo de operaciones por símbolo y día
input  int                 InpMaxTotal        = 4;               // Máximo concurrente (abiertas+pendientes). NO es diario.
input  int                 InpMaxTradesDia    = 2;               // v4.6: Máx TRADES al día en TOTAL (1 trade = 2 órdenes T1+T2)
input  int                 InpMaxParesDia     = 2;               // v4.6: Máx PARES distintos que pueden operar al día
input  double              InpMaxLoss         = 3.0;             // Pérdida diaria máxima en porcentaje para detener el EA

sinput string              _s5 = "════════ VISUAL ════════";
input  bool                InpDraw            = true;            // Dibujar rangos y elementos visuales en el gráfico
input  int                 InpHistory         = 10;              // Días históricos a dibujar
input  bool                InpDrawVWAP        = true;            // Dibujar la línea VWAP
input  bool                InpDrawLDNOpen     = true;            // Dibujar la línea de apertura de Londres
input  bool                InpDashboard       = true;            // Mostrar panel informativo en pantalla
input  color               InpClrNY15         = clrDodgerBlue;   // Color del ORB de Nueva York en 15m
input  color               InpClrNY30         = clrDodgerBlue;   // Color del ORB de Nueva York en 30m
input  color               InpClrLDN15        = clrLime;         // Color del ORB de Londres en 15m
input  color               InpClrLDN30        = clrLime;         // Color del ORB de Londres en 30m
input  color               InpClrASN15        = clrGold;         // Color del ORB de Asia en 15m
input  color               InpClrASN30        = clrGold;         // Color del ORB de Asia en 30m
input  color               InpClrLDNOpen      = clrWhite;        // Color de la línea de apertura de Londres
input  color               InpClrVWAP         = clrMagenta;      // Color de la línea VWAP

sinput string              _s6 = "════════ ALERTAS ════════";
input  bool                InpAlertPopup      = false;           // Mostrar alerta emergente
input  bool                InpAlertPush       = false;           // Enviar notificación push
input  bool                InpAlertEmail      = false;           // Enviar aviso por email

input  bool                InpVerbose         = true;            // Escribir más información en el diario/Experts
input  int                 InpMagic           = 202603;          // Magic number del EA
input  int                 InpSlip            = 10;              // Desviación máxima permitida al ejecutar órdenes

//+------------------------------------------------------------------+
//| CONSTANTS                                                         |
//+------------------------------------------------------------------+
#define SESS_NY    0
#define SESS_LDN   1
#define SESS_ASIAN 2
#define SESS_MAX   3
#define SLOTS      6   // SESS_MAX * 2 (M15 + M30 per session)

//+------------------------------------------------------------------+
//| STRUCTURES                                                        |
//+------------------------------------------------------------------+
struct SymbolData
  {
   string   symbol;
   double   rng_high[SLOTS];
   double   rng_low[SLOTS];
   bool     rng_defined[SLOTS];
   bool     rng_traded[SLOTS];
   datetime rng_time[SLOTS];
   int      fk_dir[SLOTS];
   double   fk_extreme[SLOTS];
   bool     fk_done[SLOTS];
   int      trades_today;
   bool     csi_traded;       // Already traded via CSI mode today
   double   point, pip;
   int      digits;
   double   min_lot, max_lot, lot_step;
   ENUM_ASSET_CLASS asset_class;  // v4.5: detected asset class (FX/INDEX/METAL/ENERGY)
  };

struct TradeRec
  {
   ulong  t1, t2;
   string sym;
   int    dir;
   int    sess;
   double entry;
   bool   be_done;
   double trail_best;
   string label;
  };

//+------------------------------------------------------------------+
//| GLOBALS                                                           |
//+------------------------------------------------------------------+
SymbolData  g_sym[];
int         g_cnt = 0;
string      g_names[];
TradeRec    g_tr[];
int         g_tr_cnt = 0;
CTrade      g_trade;
CPositionInfo g_pos;

double      g_day_bal = 0;
datetime    g_today = 0;
bool        g_killed = false;
int         g_gmt_off = 0;
int         g_tick = 0;

//--- v4.6: Global daily caps (resetting at DayStart rollover)
int         g_trades_today_total = 0;           // Total trades initiated today (global, all symbols)
string      g_pairs_traded_today[];             // Distinct symbols that have initiated trades today
int         g_pairs_traded_today_cnt = 0;

//--- v4.7: Effective trailing state (can be forced ON by TP2=0 runner mode)
bool        g_trail_active = false;
bool        g_runner_mode  = false;              // true when InpTP2 <= 0 → T2 has no fixed TP

int         g_start_min[SESS_MAX];
int         g_end_min[SESS_MAX];

//--- Currency Strength Meter globals
#define CSI_CURRENCIES 8
#define CSI_PAIRS      28
string      g_ccy_names[CSI_CURRENCIES] = {"EUR","USD","GBP","JPY","CHF","AUD","NZD","CAD"};
double      g_ccy_score[CSI_CURRENCIES];       // -100 to +100
int         g_ccy_rank[CSI_CURRENCIES];        // rank index (0=strongest)
string      g_csi_pairs[CSI_PAIRS];            // All 28 cross pairs
bool        g_csi_avail[CSI_PAIRS];            // Broker has this pair?
int         g_csi_base[CSI_PAIRS];             // Index into g_ccy_names for base
int         g_csi_quote[CSI_PAIRS];            // Index into g_ccy_names for quote
int         g_csi_pair_cnt = 0;                // Available pairs count
datetime    g_csi_last_calc = 0;               // Last calc bar time
double      g_csi_raw_spread = 0;              // Actual % spread between strongest/weakest
string      g_csi_conviction = "---";          // FUERTE / MEDIO / DÉBIL
string      g_ranked_syms[];                   // Ranked symbols for this session
int         g_ranked_cnt = 0;
double      g_ranked_scores[];                 // Signal scores for ranking
bool        g_rank_locked[SESS_MAX];           // Ranking locked for this session?
bool        g_csi_active = false;              // Effective CSI state (forced on by PRESET_CSI)

//+------------------------------------------------------------------+
//| ASSET CLASS DETECTION (v4.5)                                      |
//+------------------------------------------------------------------+
bool IsKnownCurrency(string c)
  {
   return (c == "EUR" || c == "USD" || c == "GBP" || c == "JPY" || c == "CHF" ||
           c == "AUD" || c == "NZD" || c == "CAD" || c == "SEK" || c == "NOK" ||
           c == "DKK" || c == "PLN" || c == "MXN" || c == "ZAR" || c == "TRY" ||
           c == "HKD" || c == "SGD" || c == "CNH" || c == "CZK" || c == "HUF");
  }

string StripSuffix(string sym)
  {
   // Remove broker suffix: .raw, .pro, .ecn, m, -STD, etc.
   // Strategy: keep chars until first non-alpha-numeric or a lowercase letter after an uppercase name
   string out = "";
   int len = StringLen(sym);
   for(int i = 0; i < len; i++)
     {
      int ch = StringGetCharacter(sym, i);
      // Keep uppercase A-Z and digits 0-9
      if((ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9'))
         out += ShortToString((ushort)ch);
      else
         break; // stop at first separator or lowercase
     }
   return out;
  }

ENUM_ASSET_CLASS DetectAssetClass(string sym)
  {
   string core = StripSuffix(sym);
   if(StringLen(core) == 0) return CLASS_UNKNOWN;

   // --- METALS ---
   if(StringFind(core, "XAU")    == 0) return CLASS_METAL;
   if(StringFind(core, "XAG")    == 0) return CLASS_METAL;
   if(StringFind(core, "XPT")    == 0) return CLASS_METAL;
   if(StringFind(core, "XPD")    == 0) return CLASS_METAL;
   if(StringFind(core, "GOLD")   == 0) return CLASS_METAL;
   if(StringFind(core, "SILVER") == 0) return CLASS_METAL;

   // --- ENERGY ---
   if(StringFind(core, "USOIL")  == 0) return CLASS_ENERGY;
   if(StringFind(core, "UKOIL")  == 0) return CLASS_ENERGY;
   if(StringFind(core, "WTI")    == 0) return CLASS_ENERGY;
   if(StringFind(core, "BRENT")  == 0) return CLASS_ENERGY;
   if(StringFind(core, "XTIUSD") == 0) return CLASS_ENERGY;
   if(StringFind(core, "XBRUSD") == 0) return CLASS_ENERGY;
   if(StringFind(core, "NATGAS") == 0) return CLASS_ENERGY;
   if(StringFind(core, "XNGUSD") == 0) return CLASS_ENERGY;

   // --- INDICES ---
   string idx_names[] = {
      "DE40","DE30","DAX40","DAX30","GER40","GER30","GERMANY40",
      "US500","SPX500","SP500","SPX","S&P500",
      "NAS100","NDX","NDX100","USTEC","US100",
      "US30","DJ30","DOW30","DOW","WS30",
      "UK100","FTSE","FTSE100",
      "JPN225","NIK225","NIKKEI","JP225",
      "FRA40","CAC40","CAC",
      "EU50","STOXX50",
      "ESP35","IBEX35","ESP",
      "AUS200","ASX200",
      "HK50","HSI","HK33"
   };
   for(int i = 0; i < ArraySize(idx_names); i++)
      if(core == idx_names[i]) return CLASS_INDEX;

   // --- FX --- (6 chars, both halves are known ISO currencies)
   if(StringLen(core) >= 6)
     {
      string b = StringSubstr(core, 0, 3);
      string q = StringSubstr(core, 3, 3);
      if(IsKnownCurrency(b) && IsKnownCurrency(q)) return CLASS_FX;
     }

   return CLASS_UNKNOWN;
  }

ENUM_ASSET_CLASS GetAssetClass(string sym)
  {
   // Prefer cached value from g_sym[] for speed
   for(int i = 0; i < g_cnt; i++)
      if(g_sym[i].symbol == sym) return g_sym[i].asset_class;
   return DetectAssetClass(sym);
  }

string AssetClassName(ENUM_ASSET_CLASS ac)
  {
   switch(ac)
     {
      case CLASS_FX:     return "FX";
      case CLASS_INDEX:  return "IDX";
      case CLASS_METAL:  return "MTL";
      case CLASS_ENERGY: return "OIL";
     }
   return "???";
  }

//--- Compute the effective "pip" unit for a symbol based on its asset class.
//    This is what InpTP1/InpMinPips/InpMaxSpread are multiplied by internally.
double ComputePipForClass(string sym, ENUM_ASSET_CLASS ac, double point, int digits)
  {
   switch(ac)
     {
      case CLASS_FX:
         return (digits == 5 || digits == 3) ? point * 10 : point;
      case CLASS_INDEX:
         // 1 "pip" = 1 index point (always intuitive for DE40, US500, etc.)
         return 1.0;
      case CLASS_METAL:
         // XAUUSD: 1 pip = $0.10 per ounce (standard forex-broker convention)
         // XAGUSD: 1 pip = $0.01 (2-digit) or $0.001 (3-digit)
         if(StringFind(sym, "XAG") >= 0 || StringFind(sym, "SILVER") >= 0)
            return (digits >= 3) ? 0.01 : 0.01;
         return 0.1;   // gold and platinum/palladium
      case CLASS_ENERGY:
         // USOIL/UKOIL: 1 pip = $0.01
         return 0.01;
     }
   // Fallback: FX-style
   return (digits == 5 || digits == 3) ? point * 10 : point;
  }

//+------------------------------------------------------------------+
//| SESSION HELPERS                                                   |
//+------------------------------------------------------------------+
bool IsSessionEnabled(int sess)
  {
   switch(InpSession)
     {
      case SESION_NY:      return sess == SESS_NY;
      case SESION_LDN:     return sess == SESS_LDN;
      case SESION_NY_LDN:  return sess == SESS_NY || sess == SESS_LDN;
      case SESION_ASIA:   return sess == SESS_ASIAN;
      case SESION_ASIA_LDN: return sess == SESS_ASIAN || sess == SESS_LDN;
      case SESION_TODAS:     return true;
     }
   return false;
  }

bool InSession(int now_min, int sess)
  {
   if(g_start_min[sess] < g_end_min[sess])
      return (now_min >= g_start_min[sess] && now_min < g_end_min[sess]);
   return (now_min >= g_start_min[sess] || now_min < g_end_min[sess]);
  }

int  TFIdx(ENUM_TIMEFRAMES tf) { return (tf == PERIOD_M15) ? 0 : 1; }

string SessTag(int s)
  {
   if(s == SESS_NY)  return "NY";
   if(s == SESS_LDN) return "LDN";
   return "ASN";
  }

color GetColor(int sess, ENUM_TIMEFRAMES tf)
  {
   if(sess == SESS_NY)    return (tf == PERIOD_M15) ? InpClrNY15  : InpClrNY30;
   if(sess == SESS_LDN)   return (tf == PERIOD_M15) ? InpClrLDN15 : InpClrLDN30;
   return (tf == PERIOD_M15) ? InpClrASN15 : InpClrASN30;
  }

bool IsDayAllowed()
  {
   MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
   switch(dt.day_of_week)
     {
      case 1: return InpMon;
      case 2: return InpTue;
      case 3: return InpWed;
      case 4: return InpThu;
      case 5: return InpFri;
     }
   return false;
  }

//+------------------------------------------------------------------+
//| INITIALIZATION                                                    |
//+------------------------------------------------------------------+
int OnInit()
  {
   BuildSymbols();
   if(g_cnt == 0) { Print("FATAL: No symbols"); return INIT_FAILED; }

   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpSlip);
   long fillMode = SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
   if((fillMode & SYMBOL_FILLING_FOK) != 0)
      g_trade.SetTypeFilling(ORDER_FILLING_FOK);
   else if((fillMode & SYMBOL_FILLING_IOC) != 0)
      g_trade.SetTypeFilling(ORDER_FILLING_IOC);
   else
      g_trade.SetTypeFilling(ORDER_FILLING_RETURN);

   ArrayResize(g_sym, g_cnt);
   for(int i = 0; i < g_cnt; i++) { CacheSym(i); ResetSym(i); }

   PreloadData();
   DetectGMT();
   CalcSessionTimes();

   g_csi_active = InpCSI || (InpPreset == PRESET_CSI) || (InpPreset == PRESET_CSI_MAJORS);
   if(g_csi_active) InitCSI();
   if(InpPreset == PRESET_CSI || InpPreset == PRESET_CSI_MAJORS)
     {
      g_csi_active = true;
      if(!InpCSI)
         Print("★ ", EnumToString(InpPreset), " → CSI activado automáticamente");
      Print("★ ", EnumToString(InpPreset), ": cargados ", g_cnt, " símbolos, operará solo los mejores ",
            IntegerToString(InpMaxPairs), " por sesión");
     }

   //--- v4.7: Runner mode detection (TP2 <= 0 means "no fixed TP for T2")
   g_runner_mode  = (InpTP2 <= 0);
   g_trail_active = InpTrail || g_runner_mode;    // trailing is mandatory when T2 runs without TP
   if(g_runner_mode)
     {
      Print("★ RUNNER MODE activo: InpTP2=", DoubleToString(InpTP2, 1),
            " → T2 se abrirá SIN TP fijo");
      if(!InpTrail)
         Print("★ RUNNER MODE: Trailing forzado a ON (sin trailing, T2 quedaría huérfano)");
      Print("★ RUNNER MODE: cuando T1 cierre por TP1, T2 pasa a BE y trailing sigue la tendencia");
     }

   g_day_bal = AccountInfoDouble(ACCOUNT_BALANCE);
   g_today   = DayStart();
   g_killed  = false;

   ArrayResize(g_tr, 0); g_tr_cnt = 0;

   TryAllRanges();
   DrawAll();
   if(InpVWAP && InpDrawVWAP) DrawVWAP();
   if(InpDashboard) DrawDashboard();

   Print("═══════ ORB v4.7 MULTI-ASSET ═══════");
   Print("  Mode: ", EnumToString(InpMode), " | Session: ", EnumToString(InpSession), " | TF: ", EnumToString(InpTF));
   Print("  Fakeout: ", EnumToString(InpFakeout), " | Dir: ", EnumToString(InpDirection));
   Print("  Trail: ", g_trail_active ? "ON" : "OFF",
         (g_runner_mode && !InpTrail) ? " (forzado por RUNNER)" : "",
         " | CloseEOS: ", InpCloseEOS ? "ON" : "OFF",
         " | Spread: ", InpMaxSpread > 0 ? DoubleToString(InpMaxSpread, 1) + "p" : "OFF");
   Print("  Caps diarios: Max ", IntegerToString(InpMaxTradesDia), " trades/día · Max ",
         IntegerToString(InpMaxParesDia), " pares/día · Max ",
         IntegerToString(InpMaxPerDay), " por símbolo/día · Max ",
         IntegerToString(InpMaxTotal), " concurrentes");
   Print("  CSI: ", InpCSI ? EnumToString(InpCSI_Mode) : "OFF",
         " (solo FX — índices/metales/petróleo no usan CSI)",
         " | MinDiff: ", DoubleToString(InpCSI_MinDiff, 0),
         " | MaxPairs: ", IntegerToString(InpMaxPairs),
         " | TF: ", EnumToString(InpCSI_TF));
   Print("  Days: ", InpMon?"Mo ":"", InpTue?"Tu ":"", InpWed?"We ":"", InpThu?"Th ":"", InpFri?"Fr":"");
   Print("  NY:  ", InpNY_H, ":", Fm(InpNY_M), " → ", g_start_min[SESS_NY] / 60, ":", Fm(g_start_min[SESS_NY] % 60), " server");
   Print("  LDN: ", InpLDN_H, ":", Fm(InpLDN_M), " → ", g_start_min[SESS_LDN] / 60, ":", Fm(g_start_min[SESS_LDN] % 60), " server");
   Print("  ASN: ", InpASN_H, ":", Fm(InpASN_M), " → ", g_start_min[SESS_ASIAN] / 60, ":", Fm(g_start_min[SESS_ASIAN] % 60), " server");
   Print("  GMT offset: +", g_gmt_off / 3600, "h | Symbols: ", g_cnt);
   //--- v4.5: list symbols grouped by asset class
   string sl_fx = "", sl_idx = "", sl_mtl = "", sl_oil = "", sl_unk = "";
   for(int i = 0; i < g_cnt; i++)
     {
      string entry = g_sym[i].symbol + " ";
      switch(g_sym[i].asset_class)
        {
         case CLASS_FX:     sl_fx  += entry; break;
         case CLASS_INDEX:  sl_idx += entry; break;
         case CLASS_METAL:  sl_mtl += entry; break;
         case CLASS_ENERGY: sl_oil += entry; break;
         default:           sl_unk += entry; break;
        }
     }
   if(StringLen(sl_fx)  > 0) Print("  FX : ", sl_fx);
   if(StringLen(sl_idx) > 0) Print("  IDX: ", sl_idx);
   if(StringLen(sl_mtl) > 0) Print("  MTL: ", sl_mtl);
   if(StringLen(sl_oil) > 0) Print("  OIL: ", sl_oil);
   if(StringLen(sl_unk) > 0) Print("  ???: ", sl_unk, " (clase no reconocida)");
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int r) { ObjectsDeleteAll(0, "ORB_"); }

//+------------------------------------------------------------------+
//| TICK                                                              |
//+------------------------------------------------------------------+
void OnTick()
  {
   //--- Daily reset
   datetime td = DayStart();
   if(td != g_today)
     {
      g_today = td; g_day_bal = AccountInfoDouble(ACCOUNT_BALANCE); g_killed = false;
      for(int i = 0; i < g_cnt; i++) ResetSym(i);
      for(int i = 0; i < SESS_MAX; i++) g_rank_locked[i] = false;
      g_csi_last_calc = 0;
      //--- v4.6: reset global daily caps
      g_trades_today_total = 0;
      ArrayResize(g_pairs_traded_today, 0);
      g_pairs_traded_today_cnt = 0;
      DetectGMT(); CalcSessionTimes(); PreloadData();
      ObjectsDeleteAll(0, "ORB_"); DrawAll();
      if(InpVWAP && InpDrawVWAP) DrawVWAP();
     }

   if(g_killed) return;
   if(!IsDayAllowed()) return;

   //--- Daily risk check
   double daily_closed = CalcDailyClosedPnL();
   double daily_float  = CalcFloatingPnL();
   double daily_total  = daily_closed + daily_float;
   double daily_pct    = (g_day_bal > 0) ? (daily_total / g_day_bal) * 100.0 : 0;

   if(daily_pct <= -InpMaxLoss)
     {
      g_killed = true;
      Print("!! DAILY LOSS LIMIT HIT | Closed=", DoubleToString(daily_closed, 2),
            " Float=", DoubleToString(daily_float, 2),
            " Total=", DoubleToString(daily_total, 2),
            " (", DoubleToString(daily_pct, 2), "% of ", DoubleToString(g_day_bal, 2), ")");
      return;
     }

   //--- Redraw on new M15 bar
   {
    static datetime sv_bar = 0;
    datetime cb = iTime(_Symbol, PERIOD_M15, 0);
    if(cb != sv_bar && cb > 0)
      {
       sv_bar = cb;
       if(InpDraw)                DrawAll();
       if(InpVWAP && InpDrawVWAP) DrawVWAP();
      }
   }

   //--- Currency Strength update (scores update live, ranking locks at session start)
   if(g_csi_active)
     {
      CalcCurrencyStrength();

      //--- Lock ranking at session start (only once per session)
      MqlDateTime stc; TimeToStruct(TimeCurrent(), stc);
      int now_csi = stc.hour * 60 + stc.min;
      for(int s = 0; s < SESS_MAX; s++)
        {
         if(!IsSessionEnabled(s)) continue;
         if(InSession(now_csi, s) && !g_rank_locked[s])
           {
            RankPairsForSession();
            g_rank_locked[s] = true;
            string log_rank = "★ CSI FIJADO " + SessTag(s) + ": ";
            int show_n = MathMin(g_ranked_cnt, InpMaxPairs);
            for(int r = 0; r < show_n; r++)
              {
               string rb, rq;
               if(SplitSymbol(g_ranked_syms[r], rb, rq))
                 {
                  int rbi = GetCcyIndex(rb), rqi = GetCcyIndex(rq);
                  double rdiff = (rbi >= 0 && rqi >= 0) ? g_ccy_score[rbi] - g_ccy_score[rqi] : 0;
                  string rdir = (rdiff > InpCSI_MinDiff) ? "▲COMPRA" : (rdiff < -InpCSI_MinDiff ? "▼VENTA" : "─NEUTRO");
                  log_rank += g_ranked_syms[r] + " " + rdir;
                 }
               else log_rank += g_ranked_syms[r];
               if(r < show_n - 1) log_rank += " | ";
              }
            if(g_ranked_cnt == 0) log_rank += "NINGUNO (sin datos)";
            Print(log_rank);
           }
        }
     }

   //--- Session checks
   MqlDateTime st; TimeToStruct(TimeCurrent(), st);
   int now = st.hour * 60 + st.min;

   ManageTrades();

   //--- End-of-session close
   if(InpCloseEOS)
     {
      for(int s = 0; s < SESS_MAX; s++)
        {
         if(!IsSessionEnabled(s)) continue;
         if(!InSession(now, s))
            CloseSessionTrades(s);
        }
     }

   g_tick++;
   if(g_tick < 5) { if(InpDashboard) DrawDashboard(); return; }
   g_tick = 0;

   //--- Process each enabled session
   for(int s = 0; s < SESS_MAX; s++)
     {
      if(!IsSessionEnabled(s)) continue;
      if(!InSession(now, s)) continue;

      for(int i = 0; i < g_cnt; i++)
        {
         if(InpTF == ORB_M15 || InpTF == ORB_AMBOS)
           {
            if(!g_sym[i].rng_defined[s*2+0]) DefRange(i, PERIOD_M15, s);
            if(g_sym[i].rng_defined[s*2+0] && !g_sym[i].rng_traded[s*2+0])
               ChkBreak(i, PERIOD_M15, s);
           }
         if(InpTF == ORB_M30 || InpTF == ORB_AMBOS)
           {
            if(!g_sym[i].rng_defined[s*2+1]) DefRange(i, PERIOD_M30, s);
            if(g_sym[i].rng_defined[s*2+1] && !g_sym[i].rng_traded[s*2+1])
               ChkBreak(i, PERIOD_M30, s);
           }
        }
     }

   if(InpDashboard) DrawDashboard();
  }

//+------------------------------------------------------------------+
//| DEFINE RANGE                                                      |
//+------------------------------------------------------------------+
void DefRange(int idx, ENUM_TIMEFRAMES tf, int sess)
  {
   string sym = g_sym[idx].symbol;
   int ti = TFIdx(tf);
   string tag = SessTag(sess) + (tf == PERIOD_M15 ? "_M15" : "_M30");

   datetime target = g_today + (datetime)(g_start_min[sess] * 60);
   int shift = iBarShift(sym, PERIOD_M15, target, false);
   if(shift < 0) return;

   int need = (tf == PERIOD_M15) ? 1 : 2;
   if(shift < need) return;

   MqlRates bars[];
   if(CopyRates(sym, PERIOD_M15, (need == 2 ? shift - 1 : shift), need, bars) != need) return;
   if(MathAbs((int)(bars[0].time - target)) > 15 * 60) return;
   if(TimeCurrent() < bars[0].time + (datetime)(need * 15 * 60)) return;

   double h, l;
   if(tf == PERIOD_M15) { h = bars[0].high; l = bars[0].low; }
   else { h = MathMax(bars[0].high, bars[1].high); l = MathMin(bars[0].low, bars[1].low); }

   double rng = (h - l) / g_sym[idx].pip;
   if(rng < InpMinPips || rng > InpMaxPips)
     { g_sym[idx].rng_defined[sess*2+ti] = true; g_sym[idx].rng_traded[sess*2+ti] = true; return; }

   g_sym[idx].rng_high[sess*2+ti] = h;
   g_sym[idx].rng_low[sess*2+ti]  = l;
   g_sym[idx].rng_defined[sess*2+ti] = true;
   g_sym[idx].rng_time[sess*2+ti] = bars[0].time;

   Print("✓ ", sym, " ", tag, " RANGE H=", DoubleToString(h, g_sym[idx].digits),
         " L=", DoubleToString(l, g_sym[idx].digits), " (", DoubleToString(rng, 1), "p)");
  }

//+------------------------------------------------------------------+
//| SPREAD CHECK                                                      |
//+------------------------------------------------------------------+
bool SpreadOK(string sym, double pip)
  {
   if(InpMaxSpread <= 0) return true;
   double spread = (SymbolInfoDouble(sym, SYMBOL_ASK) - SymbolInfoDouble(sym, SYMBOL_BID)) / pip;
   if(spread > InpMaxSpread)
     {
      if(InpVerbose)
         Print("✗ Spread | ", sym, " ", DoubleToString(spread, 1), "p > ", DoubleToString(InpMaxSpread, 1));
      return false;
     }
   return true;
  }

//+------------------------------------------------------------------+
//| CHECK BREAKOUT (ORB + Anti-ORB + fakeout + direction + spread)   |
//+------------------------------------------------------------------+
void ChkBreak(int idx, ENUM_TIMEFRAMES tf, int sess)
  {
   string sym = g_sym[idx].symbol;
   int ti = TFIdx(tf);
   int slot = sess*2+ti;
   double rh = g_sym[idx].rng_high[slot];
   double rl = g_sym[idx].rng_low[slot];
   datetime rt = g_sym[idx].rng_time[slot];
   if(rh == 0 || rl == 0) return;

   double close, candle_h, candle_l;
   datetime ct; int ps;
   if(tf == PERIOD_M15)
     {
      MqlRates r15[]; if(CopyRates(sym, PERIOD_M15, 1, 1, r15) != 1) return;
      close = r15[0].close; candle_h = r15[0].high; candle_l = r15[0].low;
      ct = r15[0].time; ps = 15 * 60;
     }
   else
     {
      MqlRates m[]; if(CopyRates(sym, PERIOD_M15, 1, 2, m) != 2) return;
      if(m[1].time - m[0].time != 15 * 60) return;
      close = m[1].close;
      candle_h = MathMax(m[0].high, m[1].high);
      candle_l = MathMin(m[0].low, m[1].low);
      ct = m[0].time; ps = 30 * 60;
     }
   if(ct <= rt) return;
   if(TimeCurrent() - (ct + ps) > ps) return;
   if(g_sym[idx].trades_today >= InpMaxPerDay) return;
   if(CountOpen() + CountPending() >= InpMaxTotal) return;
   //--- v4.6: GLOBAL DAILY CAP — max trades and distinct pairs across the whole EA
   if(!CanInitiateTrade(sym)) return;

   //--- CSI Pair Ranking: skip if this pair is not in the top N
   if(!IsPairRanked(sym)) return;

   bool in_fk_phase2 = (InpFakeout != FAKEOUT_OFF && g_sym[idx].fk_dir[slot] != 0 && !g_sym[idx].fk_done[slot]);
   bool allow_sym = (CountOpenSym(sym) == 0) || in_fk_phase2 || (InpMode == MODO_AMBOS);
   if(!allow_sym) return;

   string tag = SessTag(sess) + (tf == PERIOD_M15 ? "_M15" : "_M30");
   datetime expiry = GetSessionEnd(sess);

   //=================================================================
   // ANTI-ORB: fade the breakout (no VWAP, no fakeout, market only)
   //=================================================================
   if(InpMode == MODO_ANTI || InpMode == MODO_AMBOS)
     {
      //--- Break HIGH → SELL (fade), SL at candle high
      if(close > rh && InpDirection != DIR_SOLO_COMPRAS)
        {
         if(!SpreadOK(sym, g_sym[idx].pip)) { if(InpMode == MODO_ANTI) return; }
         else if(!IsStrengthAligned(sym, -1)) { if(InpMode == MODO_ANTI) return; }
         else
           {
            double anti_sl = NormalizeDouble(candle_h, g_sym[idx].digits);
            Print("▼ ", tag, " ANTI-ORB SELL (fade) | ", sym, " SL=", DoubleToString(anti_sl, g_sym[idx].digits));
            bool ok = ExecTrade(idx, ORDER_TYPE_SELL, anti_sl, tag + "_ANTI", sess);
            if(ok)
              {
               g_sym[idx].trades_today++;
               RegisterTradeInitiated(sym);
               if(InpMode == MODO_ANTI)
                 { g_sym[idx].rng_traded[sess*2+0] = true; g_sym[idx].rng_traded[sess*2+1] = true; }
              }
           }
        }
      //--- Break LOW → BUY (fade), SL at candle low
      if(close < rl && InpDirection != DIR_SOLO_VENTAS)
        {
         if(!SpreadOK(sym, g_sym[idx].pip)) { if(InpMode == MODO_ANTI) return; }
         else if(!IsStrengthAligned(sym, +1)) { if(InpMode == MODO_ANTI) return; }
         else
           {
            double anti_sl = NormalizeDouble(candle_l, g_sym[idx].digits);
            Print("▲ ", tag, " ANTI-ORB BUY (fade) | ", sym, " SL=", DoubleToString(anti_sl, g_sym[idx].digits));
            bool ok = ExecTrade(idx, ORDER_TYPE_BUY, anti_sl, tag + "_ANTI", sess);
            if(ok)
              {
               g_sym[idx].trades_today++;
               RegisterTradeInitiated(sym);
               if(InpMode == MODO_ANTI)
                 { g_sym[idx].rng_traded[sess*2+0] = true; g_sym[idx].rng_traded[sess*2+1] = true; }
              }
           }
        }
      //--- If pure Anti mode, stop here
      if(InpMode == MODO_ANTI) return;
     }

   //=================================================================
   // NORMAL ORB (with fakeout logic)
   //=================================================================

   //=== FAKEOUT OFF ===
   if(InpFakeout == FAKEOUT_OFF)
     {
      if(close > rh && InpDirection != DIR_SOLO_VENTAS)
        {
         if(!SpreadOK(sym, g_sym[idx].pip)) return;
         if(!IsStrengthAligned(sym, +1)) return;
         if(InpVWAP) { double v = CalcVWAP(sym); if(v > 0 && close < v) return; }
         Print("▲ ", tag, " LONG | ", sym);
         bool ok = false;
         if(InpEntry == ENTRADA_MERCADO || InpEntry == ENTRADA_AMBAS)
            ok = ExecTrade(idx, ORDER_TYPE_BUY, rl, tag, sess);
         if(InpEntry == ENTRADA_PULLBACK || InpEntry == ENTRADA_AMBAS)
           { double pb = rh + InpPBOffset * g_sym[idx].pip;
             ok = ExecPB(idx, ORDER_TYPE_BUY_LIMIT, NormalizeDouble(pb, g_sym[idx].digits), rl, tag, expiry, sess) || ok; }
         if(ok) { g_sym[idx].rng_traded[sess*2+0] = true; g_sym[idx].rng_traded[sess*2+1] = true; g_sym[idx].trades_today++; RegisterTradeInitiated(sym); }
        }
      if(close < rl && InpDirection != DIR_SOLO_COMPRAS)
        {
         if(!SpreadOK(sym, g_sym[idx].pip)) return;
         if(!IsStrengthAligned(sym, -1)) return;
         if(InpVWAP) { double v = CalcVWAP(sym); if(v > 0 && close > v) return; }
         Print("▼ ", tag, " SHORT | ", sym);
         bool ok = false;
         if(InpEntry == ENTRADA_MERCADO || InpEntry == ENTRADA_AMBAS)
            ok = ExecTrade(idx, ORDER_TYPE_SELL, rh, tag, sess);
         if(InpEntry == ENTRADA_PULLBACK || InpEntry == ENTRADA_AMBAS)
           { double pb = rl - InpPBOffset * g_sym[idx].pip;
             ok = ExecPB(idx, ORDER_TYPE_SELL_LIMIT, NormalizeDouble(pb, g_sym[idx].digits), rh, tag, expiry, sess) || ok; }
         if(ok) { g_sym[idx].rng_traded[sess*2+0] = true; g_sym[idx].rng_traded[sess*2+1] = true; g_sym[idx].trades_today++; RegisterTradeInitiated(sym); }
        }
      return;
     }

   //=== FAKEOUT MODE ===
   if(g_sym[idx].fk_dir[slot] == 0)
     {
      if(close > rh)
        {
         g_sym[idx].fk_dir[sess*2+0] = +1; g_sym[idx].fk_dir[sess*2+1] = +1;
         g_sym[idx].fk_extreme[sess*2+0] = candle_h; g_sym[idx].fk_extreme[sess*2+1] = candle_h;
         Print("⚡ ", tag, " 1st BREAK UP → trap | ", sym);
         if(InpFakeout == FAKEOUT_Y_NORMAL && InpDirection != DIR_SOLO_VENTAS)
           {
            if(!SpreadOK(sym, g_sym[idx].pip)) return;
            if(!IsStrengthAligned(sym, +1)) return;
            if(InpVWAP) { double v = CalcVWAP(sym); if(v > 0 && close < v) return; }
            bool ok = false;
            if(InpEntry == ENTRADA_MERCADO || InpEntry == ENTRADA_AMBAS)
               ok = ExecTrade(idx, ORDER_TYPE_BUY, rl, tag, sess);
            if(InpEntry == ENTRADA_PULLBACK || InpEntry == ENTRADA_AMBAS)
              { double pb = rh + InpPBOffset * g_sym[idx].pip;
                ok = ExecPB(idx, ORDER_TYPE_BUY_LIMIT, NormalizeDouble(pb, g_sym[idx].digits), rl, tag, expiry, sess) || ok; }
            if(ok) { g_sym[idx].trades_today++; RegisterTradeInitiated(sym); }
           }
        }
      else if(close < rl)
        {
         g_sym[idx].fk_dir[sess*2+0] = -1; g_sym[idx].fk_dir[sess*2+1] = -1;
         g_sym[idx].fk_extreme[sess*2+0] = candle_l; g_sym[idx].fk_extreme[sess*2+1] = candle_l;
         Print("⚡ ", tag, " 1st BREAK DOWN → trap | ", sym);
         if(InpFakeout == FAKEOUT_Y_NORMAL && InpDirection != DIR_SOLO_COMPRAS)
           {
            if(!SpreadOK(sym, g_sym[idx].pip)) return;
            if(!IsStrengthAligned(sym, -1)) return;
            if(InpVWAP) { double v = CalcVWAP(sym); if(v > 0 && close > v) return; }
            bool ok = false;
            if(InpEntry == ENTRADA_MERCADO || InpEntry == ENTRADA_AMBAS)
               ok = ExecTrade(idx, ORDER_TYPE_SELL, rh, tag, sess);
            if(InpEntry == ENTRADA_PULLBACK || InpEntry == ENTRADA_AMBAS)
              { double pb = rl - InpPBOffset * g_sym[idx].pip;
                ok = ExecPB(idx, ORDER_TYPE_SELL_LIMIT, NormalizeDouble(pb, g_sym[idx].digits), rh, tag, expiry, sess) || ok; }
            if(ok) { g_sym[idx].trades_today++; RegisterTradeInitiated(sym); }
           }
        }
      return;
     }

   //--- Phase 2: fakeout confirmation
   if(g_sym[idx].fk_done[slot]) return;
   double fk_sl = g_sym[idx].fk_extreme[slot];
   int    fk_d  = g_sym[idx].fk_dir[slot];

   if(fk_d == +1 && close < rl && InpDirection != DIR_SOLO_COMPRAS)
     {
      if(!SpreadOK(sym, g_sym[idx].pip)) return;
      if(!IsStrengthAligned(sym, -1)) return;
      if(InpVWAP) { double v = CalcVWAP(sym); if(v > 0 && close > v) return; }
      Print("▼ ", tag, " FAKEOUT SHORT | ", sym);
      bool ok = false;
      if(InpEntry == ENTRADA_MERCADO || InpEntry == ENTRADA_AMBAS)
         ok = ExecTrade(idx, ORDER_TYPE_SELL, fk_sl, tag + "_FK", sess);
      if(InpEntry == ENTRADA_PULLBACK || InpEntry == ENTRADA_AMBAS)
        { double pb = rl - InpPBOffset * g_sym[idx].pip;
          ok = ExecPB(idx, ORDER_TYPE_SELL_LIMIT, NormalizeDouble(pb, g_sym[idx].digits), fk_sl, tag + "_FK", expiry, sess) || ok; }
      if(ok)
        { g_sym[idx].fk_done[sess*2+0] = true; g_sym[idx].fk_done[sess*2+1] = true;
          g_sym[idx].rng_traded[sess*2+0] = true; g_sym[idx].rng_traded[sess*2+1] = true;
          g_sym[idx].trades_today++; RegisterTradeInitiated(sym); }
     }
   else if(fk_d == -1 && close > rh && InpDirection != DIR_SOLO_VENTAS)
     {
      if(!SpreadOK(sym, g_sym[idx].pip)) return;
      if(!IsStrengthAligned(sym, +1)) return;
      if(InpVWAP) { double v = CalcVWAP(sym); if(v > 0 && close < v) return; }
      Print("▲ ", tag, " FAKEOUT LONG | ", sym);
      bool ok = false;
      if(InpEntry == ENTRADA_MERCADO || InpEntry == ENTRADA_AMBAS)
         ok = ExecTrade(idx, ORDER_TYPE_BUY, fk_sl, tag + "_FK", sess);
      if(InpEntry == ENTRADA_PULLBACK || InpEntry == ENTRADA_AMBAS)
        { double pb = rh + InpPBOffset * g_sym[idx].pip;
          ok = ExecPB(idx, ORDER_TYPE_BUY_LIMIT, NormalizeDouble(pb, g_sym[idx].digits), fk_sl, tag + "_FK", expiry, sess) || ok; }
      if(ok)
        { g_sym[idx].fk_done[sess*2+0] = true; g_sym[idx].fk_done[sess*2+1] = true;
          g_sym[idx].rng_traded[sess*2+0] = true; g_sym[idx].rng_traded[sess*2+1] = true;
          g_sym[idx].trades_today++; RegisterTradeInitiated(sym); }
     }
  }

//+------------------------------------------------------------------+
//| ALERT                                                             |
//+------------------------------------------------------------------+
void SendAlertMsg(string msg)
  {
   if(InpAlertPopup) Alert(msg);
   if(InpAlertPush)  SendNotification(msg);
   if(InpAlertEmail) SendMail("ORB Alert", msg);
  }

//+------------------------------------------------------------------+
//| EXECUTE MARKET TRADE                                              |
//+------------------------------------------------------------------+
bool ExecTrade(int idx, ENUM_ORDER_TYPE type, double sl, string lbl, int sess)
  {
   string s = g_sym[idx].symbol; double p = g_sym[idx].pip; int d = g_sym[idx].digits;
   double ask = SymbolInfoDouble(s, SYMBOL_ASK), bid = SymbolInfoDouble(s, SYMBOL_BID);
   if(ask == 0 || bid == 0) return false;
   double ex = (type == ORDER_TYPE_BUY) ? ask : bid;
   double lot = InpLot;
   if(InpRiskPct) lot = RiskLot(s, MathAbs(ex - sl), InpRisk);
   lot = NormLot(lot, idx);
   double tp1, tp2;
   if(type == ORDER_TYPE_BUY) { tp1 = ex + InpTP1 * p; tp2 = ex + InpTP2 * p; }
   else { tp1 = ex - InpTP1 * p; tp2 = ex - InpTP2 * p; }
   sl = NormalizeDouble(sl, d); tp1 = NormalizeDouble(tp1, d); tp2 = NormalizeDouble(tp2, d);
   //--- v4.7: runner mode → T2 goes without TP (tp2 = 0 tells MT5 "no TP")
   if(g_runner_mode) tp2 = 0;

   g_trade.SetExpertMagicNumber(InpMagic);
   bool ok1 = (type == ORDER_TYPE_BUY) ? g_trade.Buy(lot, s, ex, sl, tp1, "ORB_" + lbl + "_T1")
                                        : g_trade.Sell(lot, s, ex, sl, tp1, "ORB_" + lbl + "_T1");
   ulong t1 = ok1 ? g_trade.ResultOrder() : 0;
   if(!ok1) { Print("  ✗ L1: ", g_trade.ResultRetcodeDescription()); return false; }

   bool ok2 = (type == ORDER_TYPE_BUY) ? g_trade.Buy(lot, s, ex, sl, tp2, "ORB_" + lbl + "_T2")
                                        : g_trade.Sell(lot, s, ex, sl, tp2, "ORB_" + lbl + "_T2");
   ulong t2 = ok2 ? g_trade.ResultOrder() : 0;
   if(!ok2) Print("  ✗ L2 (", g_runner_mode ? "runner" : "TP2", "): ", g_trade.ResultRetcodeDescription());

   int n = g_tr_cnt++; ArrayResize(g_tr, g_tr_cnt);
   g_tr[n].t1 = t1; g_tr[n].t2 = t2; g_tr[n].sym = s;
   g_tr[n].dir = (type == ORDER_TYPE_BUY) ? 1 : -1;
   g_tr[n].sess = sess; g_tr[n].entry = ex;
   g_tr[n].be_done = false; g_tr[n].trail_best = ex; g_tr[n].label = lbl;

   string side = (type == ORDER_TYPE_BUY) ? "BUY" : "SELL";
   string tp_info = g_runner_mode ? " [T2=RUNNER]" : "";
   Print("  ✓ ", s, " ", side, " #", t1, "/#", t2, tp_info);
   SendAlertMsg("ORB " + lbl + " " + side + " " + s + " @" + DoubleToString(ex, d));
   return true;
  }

//+------------------------------------------------------------------+
//| EXECUTE PULLBACK                                                  |
//+------------------------------------------------------------------+
bool ExecPB(int idx, ENUM_ORDER_TYPE type, double entry, double sl, string lbl, datetime exp, int sess)
  {
   string s = g_sym[idx].symbol; double p = g_sym[idx].pip; int d = g_sym[idx].digits;
   double ask = SymbolInfoDouble(s, SYMBOL_ASK), bid = SymbolInfoDouble(s, SYMBOL_BID);
   if(type == ORDER_TYPE_BUY_LIMIT && entry >= ask)
      return ExecTrade(idx, ORDER_TYPE_BUY, sl, lbl + "_PB", sess);
   if(type == ORDER_TYPE_SELL_LIMIT && entry <= bid)
      return ExecTrade(idx, ORDER_TYPE_SELL, sl, lbl + "_PB", sess);

   double lot = InpLot;
   if(InpRiskPct) lot = RiskLot(s, MathAbs(entry - sl), InpRisk);
   lot = NormLot(lot, idx);
   double tp1, tp2;
   if(type == ORDER_TYPE_BUY_LIMIT) { tp1 = entry + InpTP1 * p; tp2 = entry + InpTP2 * p; }
   else { tp1 = entry - InpTP1 * p; tp2 = entry - InpTP2 * p; }
   entry = NormalizeDouble(entry, d); sl = NormalizeDouble(sl, d);
   tp1 = NormalizeDouble(tp1, d); tp2 = NormalizeDouble(tp2, d);
   //--- v4.7: runner mode → PB2 goes without TP
   if(g_runner_mode) tp2 = 0;

   int em = (int)SymbolInfoInteger(s, SYMBOL_EXPIRATION_MODE);
   datetime oe = ((em & SYMBOL_EXPIRATION_SPECIFIED) != 0) ? exp : 0;
   ENUM_ORDER_TYPE_TIME ott = (oe > 0) ? ORDER_TIME_SPECIFIED : ORDER_TIME_GTC;

   g_trade.SetExpertMagicNumber(InpMagic);
   bool ok1 = g_trade.OrderOpen(s, type, lot, 0, entry, sl, tp1, ott, oe, "ORB_" + lbl + "_PB1");
   bool ok2 = g_trade.OrderOpen(s, type, lot, 0, entry, sl, tp2, ott, oe, "ORB_" + lbl + "_PB2");
   if(!ok1 && !ok2) return false;

   int n = g_tr_cnt++; ArrayResize(g_tr, g_tr_cnt);
   g_tr[n].t1 = ok1 ? g_trade.ResultOrder() : 0; g_tr[n].t2 = ok2 ? g_trade.ResultOrder() : 0;
   g_tr[n].sym = s; g_tr[n].dir = (type == ORDER_TYPE_BUY_LIMIT) ? 1 : -1;
   g_tr[n].sess = sess; g_tr[n].entry = entry;
   g_tr[n].be_done = false; g_tr[n].trail_best = entry; g_tr[n].label = lbl + "_PB";

   SendAlertMsg("ORB " + lbl + "_PB " + s + " LIMIT @" + DoubleToString(entry, d));
   return true;
  }

//+------------------------------------------------------------------+
//| MANAGE TRADES — BE + Trailing                                     |
//+------------------------------------------------------------------+
void ManageTrades()
  {
   for(int i = g_tr_cnt - 1; i >= 0; i--)
     {
      if(g_tr[i].t1 == 0 && g_tr[i].t2 == 0) continue;

      //--- Phase 1: TP1 hit → move T2 to BE
      if(InpBE && !g_tr[i].be_done && g_tr[i].t1 != 0)
        {
         if(!PositionSelectByTicket(g_tr[i].t1))
           {
            if(g_tr[i].t2 > 0 && PositionSelectByTicket(g_tr[i].t2))
              {
               double pip = GetPipForSym(g_tr[i].sym);
               int d = (int)SymbolInfoInteger(g_tr[i].sym, SYMBOL_DIGITS);
               double be = g_tr[i].entry + g_tr[i].dir * InpBEOff * pip;
               be = NormalizeDouble(be, d);
               double csl = PositionGetDouble(POSITION_SL);
               bool mv = (g_tr[i].dir > 0 && be > csl) || (g_tr[i].dir < 0 && (csl == 0 || be < csl));
               if(mv)
                 {
                  if(g_trade.PositionModify(g_tr[i].t2, be, PositionGetDouble(POSITION_TP)))
                    { g_tr[i].be_done = true; Print("  ✓ BE ", g_tr[i].sym, " SL→", be); }
                  else
                     Print("  ✗ BE ", g_tr[i].sym, " falló: ", g_trade.ResultRetcodeDescription());
                 }
               else
                  g_tr[i].be_done = true;   // SL ya está en mejor posición
              }
            else
               g_tr[i].be_done = true;      // T2 ya no existe, nada que mover
           }
        }

      //--- Phase 2: Trailing on T2 (uses g_trail_active, which auto-enables in runner mode)
      if(g_trail_active && g_tr[i].be_done && g_tr[i].t2 > 0 && PositionSelectByTicket(g_tr[i].t2))
        {
         double pip = GetPipForSym(g_tr[i].sym);
         int d = (int)SymbolInfoInteger(g_tr[i].sym, SYMBOL_DIGITS);
         double bid = SymbolInfoDouble(g_tr[i].sym, SYMBOL_BID);
         double ask = SymbolInfoDouble(g_tr[i].sym, SYMBOL_ASK);
         double price = (g_tr[i].dir > 0) ? bid : ask;

         if(g_tr[i].dir > 0 && price > g_tr[i].trail_best) g_tr[i].trail_best = price;
         if(g_tr[i].dir < 0 && price < g_tr[i].trail_best) g_tr[i].trail_best = price;

         double new_sl;
         if(g_tr[i].dir > 0) new_sl = g_tr[i].trail_best - InpTrailStep * pip;
         else                 new_sl = g_tr[i].trail_best + InpTrailStep * pip;
         new_sl = NormalizeDouble(new_sl, d);

         double csl = PositionGetDouble(POSITION_SL);
         bool mv = false;
         if(g_tr[i].dir > 0 && new_sl > csl) mv = true;
         if(g_tr[i].dir < 0 && (csl == 0 || new_sl < csl)) mv = true;
         if(mv) g_trade.PositionModify(g_tr[i].t2, new_sl, PositionGetDouble(POSITION_TP));
        }

      //--- Cleanup
      bool t1o = (g_tr[i].t1 > 0 && PositionSelectByTicket(g_tr[i].t1));
      bool t2o = (g_tr[i].t2 > 0 && PositionSelectByTicket(g_tr[i].t2));
      if(!t1o && !t2o) { g_tr[i].t1 = 0; g_tr[i].t2 = 0; }
     }
  }

//+------------------------------------------------------------------+
//| CLOSE SESSION TRADES                                              |
//+------------------------------------------------------------------+
void CloseSessionTrades(int sess)
  {
   for(int i = g_tr_cnt - 1; i >= 0; i--)
     {
      if(g_tr[i].sess != sess) continue;
      if(g_tr[i].t1 > 0 && PositionSelectByTicket(g_tr[i].t1))
        { g_trade.PositionClose(g_tr[i].t1); g_tr[i].t1 = 0; }
      if(g_tr[i].t2 > 0 && PositionSelectByTicket(g_tr[i].t2))
        { g_trade.PositionClose(g_tr[i].t2); g_tr[i].t2 = 0; }
     }
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong ticket = OrderGetTicket(i);
      if(ticket == 0) continue;
      if(OrderGetInteger(ORDER_MAGIC) != InpMagic) continue;
      string cmt = OrderGetString(ORDER_COMMENT);
      if(StringFind(cmt, SessTag(sess)) >= 0)
         g_trade.OrderDelete(ticket);
     }
  }

//+------------------------------------------------------------------+
//| CURRENCY STRENGTH INDEX (CSI) ENGINE                              |
//+------------------------------------------------------------------+
void InitCSI()
  {
   // Define all 28 cross pairs from 8 major currencies
   string all_pairs[CSI_PAIRS] =
     {
      "EURUSD","EURGBP","EURJPY","EURCHF","EURAUD","EURNZD","EURCAD",
      "GBPUSD","GBPJPY","GBPCHF","GBPAUD","GBPNZD","GBPCAD",
      "AUDUSD","AUDNZD","AUDJPY","AUDCHF","AUDCAD",
      "NZDUSD","NZDJPY","NZDCHF","NZDCAD",
      "USDJPY","USDCHF","USDCAD",
      "CADJPY","CADCHF",
      "CHFJPY"
     };
   // Base/Quote indices for each pair (index into g_ccy_names: EUR=0 USD=1 GBP=2 JPY=3 CHF=4 AUD=5 NZD=6 CAD=7)
   int bases[CSI_PAIRS]  = {0,0,0,0,0,0,0, 2,2,2,2,2,2, 5,5,5,5,5, 6,6,6,6, 1,1,1, 7,7, 4};
   int quotes[CSI_PAIRS] = {1,2,3,4,5,6,7, 1,3,4,5,6,7, 1,6,3,4,7, 1,3,4,7, 3,4,7, 3,4, 3};

   g_csi_pair_cnt = 0;
   for(int i = 0; i < CSI_PAIRS; i++)
     {
      g_csi_pairs[i]  = all_pairs[i];
      g_csi_base[i]   = bases[i];
      g_csi_quote[i]  = quotes[i];
      // Check if broker supports this pair — try suffix first
      string sfx_csi = StringSubstr(_Symbol, 6);
      g_csi_avail[i] = false;
      if(StringLen(sfx_csi) > 0)
        {
         string alt = all_pairs[i] + sfx_csi;
         if(SymbolSelect(alt, true) && SymbolInfoDouble(alt, SYMBOL_BID) > 0)
           { g_csi_pairs[i] = alt; g_csi_avail[i] = true; }
        }
      if(!g_csi_avail[i])
        {
         if(SymbolSelect(all_pairs[i], true) && SymbolInfoDouble(all_pairs[i], SYMBOL_BID) > 0)
            g_csi_avail[i] = true;
        }
      if(g_csi_avail[i]) g_csi_pair_cnt++;
     }
   Print("CSI: ", g_csi_pair_cnt, "/", CSI_PAIRS, " pairs available");
   string avail_list = "CSI pairs: ";
   for(int i = 0; i < CSI_PAIRS; i++)
      if(g_csi_avail[i]) avail_list += g_csi_pairs[i] + " ";
   Print(avail_list);
   ArrayInitialize(g_ccy_score, 0);
   for(int i = 0; i < CSI_CURRENCIES; i++) g_ccy_rank[i] = i;
   for(int i = 0; i < SESS_MAX; i++) g_rank_locked[i] = false;
  }

//--- Calculate strength for all 8 currencies
void CalcCurrencyStrength()
  {
   // Check if we already calculated this bar
   datetime bar_time = iTime(_Symbol, InpCSI_TF, 0);
   if(bar_time == g_csi_last_calc && g_csi_last_calc > 0) return;
   g_csi_last_calc = bar_time;

   // Reset scores
   double sum[CSI_CURRENCIES]; int cnt[CSI_CURRENCIES];
   ArrayInitialize(sum, 0); ArrayInitialize(cnt, 0);

   for(int p = 0; p < CSI_PAIRS; p++)
     {
      if(!g_csi_avail[p]) continue;
      string sym = g_csi_pairs[p];
      int b = g_csi_base[p], q = g_csi_quote[p];

      // Get rate of change over lookback period
      double c0[], cN[];
      if(CopyClose(sym, InpCSI_TF, 0, 1, c0) != 1) continue;
      if(CopyClose(sym, InpCSI_TF, InpCSI_Lookback, 1, cN) != 1) continue;
      if(cN[0] <= 0) continue;

      double roc = ((c0[0] - cN[0]) / cN[0]) * 100.0; // % change

      // Pair goes up → base strong, quote weak
      sum[b] += roc;  cnt[b]++;
      sum[q] -= roc;  cnt[q]++;
     }

   // Normalize to -100..+100
   double raw[CSI_CURRENCIES];
   double maxabs = 0;
   double raw_max = -999, raw_min = 999;
   for(int i = 0; i < CSI_CURRENCIES; i++)
     {
      raw[i] = (cnt[i] > 0) ? sum[i] / cnt[i] : 0;
      if(MathAbs(raw[i]) > maxabs) maxabs = MathAbs(raw[i]);
      if(raw[i] > raw_max) raw_max = raw[i];
      if(raw[i] < raw_min) raw_min = raw[i];
     }

   // Save real spread (% difference between strongest and weakest)
   g_csi_raw_spread = raw_max - raw_min;

   // Classify conviction
   if(g_csi_raw_spread >= 0.20)      g_csi_conviction = "FUERTE";
   else if(g_csi_raw_spread >= 0.08) g_csi_conviction = "MEDIO";
   else                               g_csi_conviction = "DÉBIL";

   if(maxabs > 0)
      for(int i = 0; i < CSI_CURRENCIES; i++)
         g_ccy_score[i] = (raw[i] / maxabs) * 100.0;
   else
      ArrayInitialize(g_ccy_score, 0);

   // Sort to get ranking (simple bubble sort, only 8 items)
   for(int i = 0; i < CSI_CURRENCIES; i++) g_ccy_rank[i] = i;
   for(int i = 0; i < CSI_CURRENCIES - 1; i++)
      for(int j = i + 1; j < CSI_CURRENCIES; j++)
         if(g_ccy_score[g_ccy_rank[j]] > g_ccy_score[g_ccy_rank[i]])
           { int tmp = g_ccy_rank[i]; g_ccy_rank[i] = g_ccy_rank[j]; g_ccy_rank[j] = tmp; }

   if(InpVerbose)
     {
      string log = "CSI: ";
      for(int i = 0; i < CSI_CURRENCIES; i++)
         log += g_ccy_names[g_ccy_rank[i]] + "(" + DoubleToString(g_ccy_score[g_ccy_rank[i]], 1) + ") ";
      log += "| Spread:" + DoubleToString(g_csi_raw_spread, 3) + "% " + g_csi_conviction;
      Print(log);
     }
  }

//--- Get currency index from 3-letter code
int GetCcyIndex(string ccy)
  {
   for(int i = 0; i < CSI_CURRENCIES; i++)
      if(g_ccy_names[i] == ccy) return i;
   return -1;
  }

//--- Extract base and quote currency from a symbol name
bool SplitSymbol(string sym, string &base, string &quote)
  {
   // Strip broker suffix
   string core = sym;
   if(StringLen(core) > 6) core = StringSubstr(core, 0, 6);
   if(StringLen(core) < 6) return false;
   base  = StringSubstr(core, 0, 3);
   quote = StringSubstr(core, 3, 3);
   return (GetCcyIndex(base) >= 0 && GetCcyIndex(quote) >= 0);
  }

//--- Check if currency strength supports the trade direction
//    dir: +1 = BUY (need base stronger than quote), -1 = SELL (need quote stronger)
bool IsStrengthAligned(string sym, int dir)
  {
   if(!g_csi_active) return true;
   //--- v4.5: skip CSI for non-FX symbols (indices, metals, energy)
   if(GetAssetClass(sym) != CLASS_FX) return true;
   if(InpCSI_Mode == CSI_SOLO_INFO && InpPreset != PRESET_CSI && InpPreset != PRESET_CSI_MAJORS) return true;

   // Conviction check: if real spread is too low, no edge
   if(InpCSI_MinConv > 0 && g_csi_raw_spread < InpCSI_MinConv)
     {
      if(InpVerbose)
         Print("✗ CSI | ", sym, " bloqueado: señal DÉBIL (spread real ",
               DoubleToString(g_csi_raw_spread, 3), "% < ", DoubleToString(InpCSI_MinConv, 3), "%)");
      return false;
     }

   string base, quote;
   if(!SplitSymbol(sym, base, quote)) return true; // unknown pair, allow

   int bi = GetCcyIndex(base), qi = GetCcyIndex(quote);
   if(bi < 0 || qi < 0) return true;

   double diff = g_ccy_score[bi] - g_ccy_score[qi];

   // BUY: base must be stronger than quote by MinDiff
   if(dir > 0 && diff < InpCSI_MinDiff)
     {
      if(InpVerbose)
         Print("✗ CSI | ", sym, " BUY blocked: ", g_ccy_names[bi], "=", DoubleToString(g_ccy_score[bi], 1),
               " vs ", g_ccy_names[qi], "=", DoubleToString(g_ccy_score[qi], 1),
               " diff=", DoubleToString(diff, 1), " < ", DoubleToString(InpCSI_MinDiff, 1));
      return false;
     }
   // SELL: quote must be stronger than base by MinDiff
   if(dir < 0 && diff > -InpCSI_MinDiff)
     {
      if(InpVerbose)
         Print("✗ CSI | ", sym, " SELL blocked: ", g_ccy_names[bi], "=", DoubleToString(g_ccy_score[bi], 1),
               " vs ", g_ccy_names[qi], "=", DoubleToString(g_ccy_score[qi], 1),
               " diff=", DoubleToString(diff, 1), " > ", DoubleToString(-InpCSI_MinDiff, 1));
      return false;
     }
   return true;
  }

//--- Rank all active symbols by signal quality for current session
void RankPairsForSession()
  {
   if(!g_csi_active) return;

   ArrayResize(g_ranked_syms, g_cnt);
   ArrayResize(g_ranked_scores, g_cnt);
   g_ranked_cnt = 0;

   for(int i = 0; i < g_cnt; i++)
     {
      string sym = g_sym[i].symbol;
      //--- v4.5: skip non-FX from CSI ranking
      if(g_sym[i].asset_class != CLASS_FX) continue;
      string base, quote;
      if(!SplitSymbol(sym, base, quote)) continue;

      int bi = GetCcyIndex(base), qi = GetCcyIndex(quote);
      if(bi < 0 || qi < 0) continue;

      // Signal score = absolute strength differential
      // Higher = clearer directional edge
      double diff = MathAbs(g_ccy_score[bi] - g_ccy_score[qi]);

      // Bonus: if one of the currencies is #1 strongest or weakest, add weight
      double bonus = 0;
      if(g_ccy_rank[0] == bi || g_ccy_rank[0] == qi) bonus += 10;
      if(g_ccy_rank[CSI_CURRENCIES - 1] == bi || g_ccy_rank[CSI_CURRENCIES - 1] == qi) bonus += 10;

      // VWAP alignment bonus
      if(InpVWAP)
        {
         double v = CalcVWAP(sym);
         if(v > 0)
           {
            double bid = SymbolInfoDouble(sym, SYMBOL_BID);
            double base_score = g_ccy_score[bi], quote_score = g_ccy_score[qi];
            // If CSI says BUY and price is above VWAP, good alignment
            if(base_score > quote_score && bid > v) bonus += 15;
            // If CSI says SELL and price is below VWAP
            if(base_score < quote_score && bid < v) bonus += 15;
           }
        }

      g_ranked_syms[g_ranked_cnt] = sym;
      g_ranked_scores[g_ranked_cnt] = diff + bonus;
      g_ranked_cnt++;
     }

   // Sort by score descending (bubble sort, max 7 items)
   for(int i = 0; i < g_ranked_cnt - 1; i++)
      for(int j = i + 1; j < g_ranked_cnt; j++)
         if(g_ranked_scores[j] > g_ranked_scores[i])
           {
            string ts = g_ranked_syms[i]; g_ranked_syms[i] = g_ranked_syms[j]; g_ranked_syms[j] = ts;
            double td = g_ranked_scores[i]; g_ranked_scores[i] = g_ranked_scores[j]; g_ranked_scores[j] = td;
           }

   if(InpVerbose && g_ranked_cnt > 0)
     {
      string log = "RANK: ";
      for(int i = 0; i < MathMin(g_ranked_cnt, InpMaxPairs + 2); i++)
         log += IntegerToString(i + 1) + "." + g_ranked_syms[i] + "(" + DoubleToString(g_ranked_scores[i], 1) + ") ";
      Print(log);
     }
  }

//--- Check if a symbol is within the top N ranked pairs
bool IsPairRanked(string sym)
  {
   if(!g_csi_active) return true;
   //--- v4.5: non-FX instruments don't compete for CSI ranking slots
   if(GetAssetClass(sym) != CLASS_FX) return true;
   // PRESET_CSI / PRESET_CSI_MAJORS: always enforce ranking regardless of mode
   if(InpCSI_Mode == CSI_SOLO_INFO && InpPreset != PRESET_CSI && InpPreset != PRESET_CSI_MAJORS) return true;
   if(InpCSI_Mode == CSI_FILTRO && InpMaxPairs >= g_cnt && InpPreset != PRESET_CSI && InpPreset != PRESET_CSI_MAJORS) return true;

   int limit = MathMin(InpMaxPairs, g_ranked_cnt);

   // If ranking not yet calculated, block trades (wait for session start)
   if(g_ranked_cnt == 0)
     {
      if(InpVerbose)
         Print("✗ RANK | ", sym, " bloqueado: ranking aún no calculado");
      return false;
     }

   for(int i = 0; i < limit; i++)
      if(g_ranked_syms[i] == sym) return true;

   if(InpVerbose)
      Print("✗ RANK | ", sym, " no está en el top ", IntegerToString(InpMaxPairs));
   return false;
  }

//+------------------------------------------------------------------+
//| VWAP                                                              |
//+------------------------------------------------------------------+
double CalcVWAP(string sym)
  {
   MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
   if(InpVWAP_Anchor == 1) dt.hour = 8 + g_gmt_off / 3600;
   else if(InpVWAP_Anchor == 2) dt.hour = g_gmt_off / 3600;
   else dt.hour = 0;
   dt.min = 0; dt.sec = 0;
   datetime anc = StructToTime(dt);
   if(anc > TimeCurrent()) anc -= 86400;
   MqlRates r[];
   int n = CopyRates(sym, InpVWAP_TF, anc, TimeCurrent(), r);
   if(n < 1) return 0;
   double ctpv = 0, cvol = 0;
   for(int i = 0; i < n; i++)
     { double tp = (r[i].high + r[i].low + r[i].close) / 3.0;
       double v = (double)r[i].tick_volume; if(v <= 0) v = 1;
       ctpv += tp * v; cvol += v; }
   return (cvol > 0) ? ctpv / cvol : 0;
  }

void DrawVWAP()
  {
   string sym = _Symbol;
   int digs = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   ObjectsDeleteAll(0, "ORB_VW_");
   int ahs = 0;
   if(InpVWAP_Anchor == 1) ahs = 8 + g_gmt_off / 3600;
   else if(InpVWAP_Anchor == 2) ahs = g_gmt_off / 3600;

   int days = InpVWAP_Days + 1;
   datetime tm = DayStart();
   int sid = 0;

   for(int d = 0; d < days; d++)
     {
      datetime dm = tm - (datetime)(d * 86400);
      MqlDateTime ds; TimeToStruct(dm, ds);
      if(ds.day_of_week == 0 || ds.day_of_week == 6) { days++; if(days > InpVWAP_Days + 10) break; continue; }

      MqlDateTime ad; TimeToStruct(dm, ad);
      ad.hour = ahs; ad.min = 0; ad.sec = 0;
      datetime as2 = StructToTime(ad);
      datetime ae;
      if(d == 0) ae = TimeCurrent();
      else
        { datetime nm = dm + 86400; MqlDateTime nd; TimeToStruct(nm, nd);
          while(nd.day_of_week == 0 || nd.day_of_week == 6) { nm += 86400; TimeToStruct(nm, nd); }
          nd.hour = ahs; nd.min = 0; nd.sec = 0; ae = StructToTime(nd); }

      MqlRates r[];
      int n = CopyRates(sym, InpVWAP_TF, as2, ae, r);
      if(n < 2) continue;
      double ct2 = 0, cv = 0, pv = 0; datetime pt = 0;
      int w = (d == 0) ? 2 : 1;
      for(int i = 0; i < n; i++)
        { double tp = (r[i].high + r[i].low + r[i].close) / 3.0;
          double v = (double)r[i].tick_volume; if(v <= 0) v = 1;
          ct2 += tp * v; cv += v; double vw = ct2 / cv;
          if(i > 0 && pv > 0)
            { string sg = "ORB_VW_" + IntegerToString(sid++);
              ObjectCreate(0, sg, OBJ_TREND, 0, pt, pv, r[i].time, vw);
              ObjectSetInteger(0, sg, OBJPROP_COLOR, InpClrVWAP);
              ObjectSetInteger(0, sg, OBJPROP_STYLE, STYLE_SOLID);
              ObjectSetInteger(0, sg, OBJPROP_WIDTH, w);
              ObjectSetInteger(0, sg, OBJPROP_RAY_RIGHT, false);
              ObjectSetInteger(0, sg, OBJPROP_BACK, false);
              ObjectSetInteger(0, sg, OBJPROP_SELECTABLE, false); }
          pv = vw; pt = r[i].time; }
      if(d == 0 && pv > 0)
        { string lb = "ORB_VW_lbl"; ObjectDelete(0, lb);
          ObjectCreate(0, lb, OBJ_TEXT, 0, TimeCurrent(), pv);
          ObjectSetString(0, lb, OBJPROP_TEXT, " ◆ VWAP " + DoubleToString(pv, digs));
          ObjectSetInteger(0, lb, OBJPROP_COLOR, InpClrVWAP);
          ObjectSetInteger(0, lb, OBJPROP_FONTSIZE, 11);
          ObjectSetString(0, lb, OBJPROP_FONT, "Arial Bold"); }
     }
   ChartRedraw(0);
  }

//+------------------------------------------------------------------+
//| DRAW ALL                                                          |
//+------------------------------------------------------------------+
void DrawAll()
  {
   if(!InpDraw) return;
   string sym = _Symbol;
   int digs = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   double pt = SymbolInfoDouble(sym, SYMBOL_POINT);
   //--- v4.5: asset-class-aware pip (DE40=1pt, XAUUSD=0.1, USOIL=0.01, FX=standard)
   ENUM_ASSET_CLASS chart_ac = DetectAssetClass(sym);
   double pip = ComputePipForClass(sym, chart_ac, pt, digs);
   MqlRates pre[]; CopyRates(sym, PERIOD_M15, 0, 2000, pre);
   int days = InpHistory + 1;
   datetime today = DayStart();

   for(int d = 0; d < days; d++)
     {
      datetime dm = today - (datetime)(d * 86400);
      MqlDateTime ds; TimeToStruct(dm, ds);
      if(ds.day_of_week == 0 || ds.day_of_week == 6) { days++; if(days > InpHistory + 20) break; continue; }

      for(int sess = 0; sess < SESS_MAX; sess++)
        {
         datetime target = dm + (datetime)(g_start_min[sess] * 60);
         MqlDateTime se; TimeToStruct(target, se);
         se.hour = g_end_min[sess] / 60; se.min = g_end_min[sess] % 60; se.sec = 0;
         datetime send = StructToTime(se);

         int shift = iBarShift(sym, PERIOD_M15, target, false);
         if(shift < 0) continue;
         MqlRates bars[];
         int got = CopyRates(sym, PERIOD_M15, shift - 1, 2, bars);
         if(got < 1) continue;
         if(MathAbs((int)(bars[0].time - target)) > 15 * 60) continue;

         if(InpTF == ORB_M15 || InpTF == ORB_AMBOS)
           { if(TimeCurrent() >= bars[0].time + 15 * 60)
               { double rng = (bars[0].high - bars[0].low) / pip;
                 if(rng >= InpMinPips && rng <= InpMaxPips)
                    DrawBox(bars[0].time, bars[0].high, bars[0].low, PERIOD_M15, send, digs, d == 0, sess); } }
         if((InpTF == ORB_M30 || InpTF == ORB_AMBOS) && got >= 2)
           { if(TimeCurrent() >= bars[0].time + 30 * 60)
               { double h = MathMax(bars[0].high, bars[1].high);
                 double l = MathMin(bars[0].low, bars[1].low);
                 double rng = (h - l) / pip;
                 if(rng >= InpMinPips && rng <= InpMaxPips)
                    DrawBox(bars[0].time, h, l, PERIOD_M30, send, digs, d == 0, sess); } }
        }
      if(InpDrawLDNOpen)
        { datetime lo = dm + (datetime)(g_start_min[SESS_LDN] * 60);
          DrawLDNOpen(lo, d == 0, digs); }
     }
   ChartRedraw(0);
  }

//+------------------------------------------------------------------+
//| DRAW BOX                                                          |
//+------------------------------------------------------------------+
void DrawBox(datetime bt, double h, double l, ENUM_TIMEFRAMES tf,
             datetime send, int digs, bool today, int sess)
  {
   string stag = SessTag(sess);
   string tftag = (tf == PERIOD_M15) ? "15" : "30";
   color clr = GetColor(sess, tf);
   int tfs = PeriodSeconds(tf);
   datetime be = bt + (datetime)tfs;
   string tag = "ORB_" + stag + tftag + "_" + TimeToString(bt, TIME_DATE | TIME_MINUTES);
   StringReplace(tag, ":", ""); StringReplace(tag, " ", "_");
   int lw = today ? 2 : 1;

   if(tf == PERIOD_M15)
     { string bx = tag + "_box"; ObjectDelete(0, bx);
       ObjectCreate(0, bx, OBJ_RECTANGLE, 0, bt, h, be, l);
       ObjectSetInteger(0, bx, OBJPROP_COLOR, clr); ObjectSetInteger(0, bx, OBJPROP_FILL, true);
       ObjectSetInteger(0, bx, OBJPROP_BACK, true); ObjectSetInteger(0, bx, OBJPROP_SELECTABLE, false); }

   string hn = tag + "_H"; ObjectDelete(0, hn);
   ObjectCreate(0, hn, OBJ_TREND, 0, (tf == PERIOD_M15 ? be : bt), h, send, h);
   ObjectSetInteger(0, hn, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, hn, OBJPROP_STYLE, (tf == PERIOD_M15 && !today) ? STYLE_DOT : STYLE_DASH);
   ObjectSetInteger(0, hn, OBJPROP_WIDTH, lw);
   ObjectSetInteger(0, hn, OBJPROP_RAY_RIGHT, false); ObjectSetInteger(0, hn, OBJPROP_SELECTABLE, false);

   string ln = tag + "_L"; ObjectDelete(0, ln);
   ObjectCreate(0, ln, OBJ_TREND, 0, (tf == PERIOD_M15 ? be : bt), l, send, l);
   ObjectSetInteger(0, ln, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, ln, OBJPROP_STYLE, (tf == PERIOD_M15 && !today) ? STYLE_DOT : STYLE_DASH);
   ObjectSetInteger(0, ln, OBJPROP_WIDTH, lw);
   ObjectSetInteger(0, ln, OBJPROP_RAY_RIGHT, false); ObjectSetInteger(0, ln, OBJPROP_SELECTABLE, false);

   if(today)
     {
      string lh = tag + "_LH"; ObjectDelete(0, lh);
      ObjectCreate(0, lh, OBJ_TEXT, 0, send, h);
      ObjectSetString(0, lh, OBJPROP_TEXT, " " + stag + (tf == PERIOD_M15 ? " M15" : " M30") + " H " + DoubleToString(h, digs));
      ObjectSetInteger(0, lh, OBJPROP_COLOR, clr); ObjectSetInteger(0, lh, OBJPROP_FONTSIZE, 8);
      ObjectSetString(0, lh, OBJPROP_FONT, "Arial Bold"); ObjectSetInteger(0, lh, OBJPROP_ANCHOR, ANCHOR_LEFT_LOWER);

      string ll = tag + "_LL"; ObjectDelete(0, ll);
      ObjectCreate(0, ll, OBJ_TEXT, 0, send, l);
      ObjectSetString(0, ll, OBJPROP_TEXT, " " + stag + (tf == PERIOD_M15 ? " M15" : " M30") + " L " + DoubleToString(l, digs));
      ObjectSetInteger(0, ll, OBJPROP_COLOR, clr); ObjectSetInteger(0, ll, OBJPROP_FONTSIZE, 8);
      ObjectSetString(0, ll, OBJPROP_FONT, "Arial Bold"); ObjectSetInteger(0, ll, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
     }
  }

//+------------------------------------------------------------------+
//| DRAW LDN OPEN                                                    |
//+------------------------------------------------------------------+
void DrawLDNOpen(datetime ldn_time, bool today, int digs)
  {
   int shift = iBarShift(_Symbol, PERIOD_M15, ldn_time, false);
   if(shift < 0) return;
   MqlRates r[];
   if(CopyRates(_Symbol, PERIOD_M15, shift, 1, r) != 1) return;
   if(MathAbs((int)(r[0].time - ldn_time)) > 15 * 60) return;
   if(TimeCurrent() < r[0].time + 15 * 60) return;

   string day = TimeToString(r[0].time, TIME_DATE);
   int lw = today ? 2 : 1;

   string vl = "ORB_LDNopen_" + day; ObjectDelete(0, vl);
   ObjectCreate(0, vl, OBJ_VLINE, 0, r[0].time, 0);
   ObjectSetInteger(0, vl, OBJPROP_COLOR, InpClrLDNOpen); ObjectSetInteger(0, vl, OBJPROP_STYLE, STYLE_DOT);
   ObjectSetInteger(0, vl, OBJPROP_WIDTH, 1); ObjectSetInteger(0, vl, OBJPROP_BACK, true);
   ObjectSetInteger(0, vl, OBJPROP_SELECTABLE, false);

   string ar = "ORB_LDNarr_" + day; ObjectDelete(0, ar);
   ObjectCreate(0, ar, OBJ_ARROW_DOWN, 0, r[0].time, r[0].high);
   ObjectSetInteger(0, ar, OBJPROP_COLOR, InpClrLDNOpen); ObjectSetInteger(0, ar, OBJPROP_WIDTH, lw);
   ObjectSetInteger(0, ar, OBJPROP_SELECTABLE, false);

   if(today)
     { string lb = "ORB_LDNlbl_" + day; ObjectDelete(0, lb);
       ObjectCreate(0, lb, OBJ_TEXT, 0, r[0].time, r[0].high);
       ObjectSetString(0, lb, OBJPROP_TEXT, " LDN OPEN");
       ObjectSetInteger(0, lb, OBJPROP_COLOR, InpClrLDNOpen); ObjectSetInteger(0, lb, OBJPROP_FONTSIZE, 9);
       ObjectSetString(0, lb, OBJPROP_FONT, "Arial Bold"); ObjectSetInteger(0, lb, OBJPROP_ANCHOR, ANCHOR_LEFT_LOWER); }
  }

//+------------------------------------------------------------------+
//| DASHBOARD                                                         |
//+------------------------------------------------------------------+
void DrawDashboard()
  {
   int x = 12, y = 28, dy = 19;
   string pf = "ORB_DASH_";
   int ln = 0;

   // Calculate dynamic height based on CSI
   int base_h = 295;  // v4.6: +20 for daily cap line
   if(g_csi_active) base_h += 230; // extra space for CSI + conviction + ranking

   string bg = pf + "BG"; ObjectDelete(0, bg);
   ObjectCreate(0, bg, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, bg, OBJPROP_XDISTANCE, x - 6); ObjectSetInteger(0, bg, OBJPROP_YDISTANCE, y - 6);
   ObjectSetInteger(0, bg, OBJPROP_XSIZE, 345); ObjectSetInteger(0, bg, OBJPROP_YSIZE, base_h);
   ObjectSetInteger(0, bg, OBJPROP_BGCOLOR, C'20,20,30');
   ObjectSetInteger(0, bg, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, bg, OBJPROP_BORDER_COLOR, C'60,60,80');
   ObjectSetInteger(0, bg, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, bg, OBJPROP_BACK, false); ObjectSetInteger(0, bg, OBJPROP_SELECTABLE, false);

   DL(pf, ln++, x, y, "ORB v4.7 | " + EnumToString(InpSession), clrWhite, 11); y += dy + 3;

   //--- v4.5: asset class summary
   int n_fx=0, n_idx=0, n_mtl=0, n_oil=0;
   for(int i = 0; i < g_cnt; i++)
     {
      switch(g_sym[i].asset_class)
        {
         case CLASS_FX:     n_fx++;  break;
         case CLASS_INDEX:  n_idx++; break;
         case CLASS_METAL:  n_mtl++; break;
         case CLASS_ENERGY: n_oil++; break;
        }
     }
   string ac_line = "";
   if(n_fx  > 0) ac_line += "FX:"  + IntegerToString(n_fx)  + "  ";
   if(n_idx > 0) ac_line += "IDX:" + IntegerToString(n_idx) + "  ";
   if(n_mtl > 0) ac_line += "MTL:" + IntegerToString(n_mtl) + "  ";
   if(n_oil > 0) ac_line += "OIL:" + IntegerToString(n_oil);
   if(StringLen(ac_line) > 0)
     { DL(pf, ln++, x, y, ac_line, clrCyan, 9); y += dy; }

   //--- Mode line
   string ms = "ORB"; if(InpMode == MODO_ANTI) ms = "ANTI-ORB"; if(InpMode == MODO_AMBOS) ms = "ORB+ANTI";
   color mc = (InpMode == MODO_ANTI) ? clrOrangeRed : (InpMode == MODO_AMBOS ? clrGold : clrDodgerBlue);
   string ds = "Both"; if(InpDirection == DIR_SOLO_COMPRAS) ds = "Buys"; if(InpDirection == DIR_SOLO_VENTAS) ds = "Sells";
   DL(pf, ln++, x, y, "Mode:" + ms + " | Dir:" + ds, mc, 9); y += dy;

   string fs = "OFF"; if(InpFakeout == FAKEOUT_SOLO) fs = "FKonly"; if(InpFakeout == FAKEOUT_Y_NORMAL) fs = "FK+Norm";
   DL(pf, ln++, x, y, "FK:" + fs + " | Sprd:" + (InpMaxSpread > 0 ? DoubleToString(InpMaxSpread, 1) + "p" : "OFF"), C'180,180,200', 9); y += dy;
   DL(pf, ln++, x, y, "Trail:" + (g_trail_active ? DoubleToString(InpTrailStep, 0) + "p" : "OFF") + (g_runner_mode ? " [RUNNER]" : "") + " | EOS:" + (InpCloseEOS ? "ON" : "OFF"), C'180,180,200', 9); y += dy + 4;

   for(int s = 0; s < SESS_MAX; s++)
     {
      if(!IsSessionEnabled(s)) continue;
      MqlDateTime st; TimeToStruct(TimeCurrent(), st);
      int now = st.hour * 60 + st.min;
      bool live = InSession(now, s);
      color sc = live ? clrLime : C'120,120,140';
      DL(pf, ln++, x, y, SessTag(s) + (live ? " ● LIVE" : " ○ idle"), sc, 9); y += dy;
     }
   y += 3;

   DL(pf, ln++, x, y, "Open:" + IntegerToString(CountOpen()) + "/" + IntegerToString(InpMaxTotal)
      + "  Pend:" + IntegerToString(CountPending()), C'180,180,200', 9); y += dy;

   //--- v4.6: daily cap indicator
   color cap_color = C'180,180,200';
   if(g_trades_today_total >= InpMaxTradesDia || g_pairs_traded_today_cnt >= InpMaxParesDia)
      cap_color = clrOrange;
   DL(pf, ln++, x, y, "Hoy: " + IntegerToString(g_trades_today_total) + "/" + IntegerToString(InpMaxTradesDia)
      + " trades  " + IntegerToString(g_pairs_traded_today_cnt) + "/" + IntegerToString(InpMaxParesDia) + " pares",
      cap_color, 9); y += dy;

   double dc = CalcDailyClosedPnL(), df = CalcFloatingPnL(), dt = dc + df;
   double dp = (g_day_bal > 0) ? (dt / g_day_bal) * 100.0 : 0;
   DL(pf, ln++, x, y, "P&L: $" + DoubleToString(dt, 2) + " (" + DoubleToString(dp, 2) + "%)",
      (dt >= 0) ? clrLime : clrOrangeRed, 10); y += dy;

   double rem = InpMaxLoss + dp;
   DL(pf, ln++, x, y, "Limit left: " + DoubleToString(rem, 2) + "%",
      (rem > 1.0) ? C'180,180,200' : clrOrangeRed, 9);

   //--- CURRENCY STRENGTH METER ---
   if(g_csi_active)
     {
      y += dy + 6;
      DL(pf, ln++, x, y, "── CURRENCY STRENGTH ──", clrCyan, 9); y += dy + 2;

      // Show all 8 currencies ranked from strongest to weakest
      for(int i = 0; i < CSI_CURRENCIES; i++)
        {
         int ci = g_ccy_rank[i];
         double sc2 = g_ccy_score[ci];

         // Color gradient: strong=green, neutral=gray, weak=red
         color csi_clr;
         if(sc2 > 30)       csi_clr = clrLime;
         else if(sc2 > 10)  csi_clr = clrSpringGreen;
         else if(sc2 > -10) csi_clr = C'180,180,200';
         else if(sc2 > -30) csi_clr = clrOrange;
         else               csi_clr = clrOrangeRed;

         // Build visual bar (max 10 chars)
         int bar_len = (int)MathRound(MathAbs(sc2) / 10.0);
         if(bar_len > 10) bar_len = 10;
         string bar = "";
         for(int b = 0; b < bar_len; b++) bar += "█";

         string prefix = (sc2 >= 0) ? "+" : "";
         DL(pf, ln++, x, y,
            IntegerToString(i + 1) + ". " + g_ccy_names[ci] + " " + prefix + DoubleToString(sc2, 1) + " " + bar,
            csi_clr, 9);
         y += dy;
        }

      //--- Conviction indicator (visual signal meter, no numbers)
      y += 2;
      color conv_clr = clrLime;
      string bar_full = "█"; string bar_empty = "░";
      int bars = 1; // minimum 1 bar
      if(g_csi_raw_spread >= 0.04) bars = 2;
      if(g_csi_raw_spread >= 0.08) bars = 3;
      if(g_csi_raw_spread >= 0.15) bars = 4;
      if(g_csi_raw_spread >= 0.25) bars = 5;
      if(bars <= 2) conv_clr = clrOrangeRed;
      else if(bars <= 3) conv_clr = clrGold;

      string meter = "";
      for(int bb = 0; bb < 5; bb++) meter += (bb < bars) ? bar_full : bar_empty;

      DL(pf, ln++, x, y, meter + "  " + g_csi_conviction, conv_clr, 10);
      y += dy;

      //--- PAIR RANKING ---
      y += 4;
      DL(pf, ln++, x, y, "── MEJORES PARES ──", clrCyan, 9); y += dy + 2;

      int show = MathMin(g_ranked_cnt, MathMin(InpMaxPairs + 1, 7));
      double top_score = (g_ranked_cnt > 0) ? g_ranked_scores[0] : 1;
      if(top_score <= 0) top_score = 1;

      for(int i = 0; i < show; i++)
        {
         bool active = (i < InpMaxPairs);
         string base2, quote2;
         string dir_txt = "";
         color dir_clr = C'100,100,120';

         if(SplitSymbol(g_ranked_syms[i], base2, quote2))
           {
            int bi2 = GetCcyIndex(base2), qi2 = GetCcyIndex(quote2);
            if(bi2 >= 0 && qi2 >= 0)
              {
               double diff = g_ccy_score[bi2] - g_ccy_score[qi2];
               if(diff > InpCSI_MinDiff)       { dir_txt = " ▲ COMPRA"; dir_clr = clrLime; }
               else if(diff < -InpCSI_MinDiff)  { dir_txt = " ▼ VENTA";  dir_clr = clrOrangeRed; }
               else                              { dir_txt = " ─ NEUTRO"; dir_clr = C'180,180,200'; }
              }
           }

         // Stars based on relative score strength
         double pct = g_ranked_scores[i] / top_score * 100.0;
         string stars = "★☆☆";
         if(pct >= 66) stars = "★★★";
         else if(pct >= 33) stars = "★★☆";

         if(!active) { dir_clr = C'100,100,120'; stars = ""; }

         DL(pf, ln++, x, y,
            IntegerToString(i + 1) + ". " + g_ranked_syms[i] + dir_txt + "  " + stars,
            dir_clr, 9);
         y += dy;
        }
     }

   ChartRedraw(0);
  }

void DL(string pf, int idx, int x, int y, string text, color clr, int sz)
  {
   string nm = pf + IntegerToString(idx);
   ObjectDelete(0, nm);
   ObjectCreate(0, nm, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetString(0, nm, OBJPROP_TEXT, text);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, clr); ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, sz);
   ObjectSetString(0, nm, OBJPROP_FONT, "Consolas");
   ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
  }

//+------------------------------------------------------------------+
//| UTILITY                                                           |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| MULTI-ASSET ALIAS RESOLVER (v4.5)                                 |
//| Tries common broker naming variants for non-FX instruments.        |
//| Returns the actual symbol name found in Market Watch, or "" if nope.|
//+------------------------------------------------------------------+
string ResolveSymbolAlias(string base, string sfx)
  {
   //--- Build list of candidate names to try
   string alts[];
   ArrayResize(alts, 0);

   //--- Direct + suffix variants for the base itself
   if(StringLen(sfx) > 0)
     { ArrayResize(alts, ArraySize(alts) + 1); alts[ArraySize(alts) - 1] = base + sfx; }
   ArrayResize(alts, ArraySize(alts) + 1); alts[ArraySize(alts) - 1] = base;

   //--- Alias lookup table for indices / metals / energy
   string aliases[];
   ArrayResize(aliases, 0);

   if(base == "DE40" || base == "DAX" || base == "GER40" || base == "DE30" ||
      base == "DAX40" || base == "GERMANY40")
     { string a[] = {"DE40","GER40","DAX40","DE30","GER30","DAX30","GERMANY40","GERMANY30","DAX"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "US500" || base == "SPX500" || base == "SPX" || base == "SP500")
     { string a[] = {"US500","SPX500","SPX","SP500","US500Cash","SPX500Cash"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "NAS100" || base == "NDX" || base == "USTEC" || base == "US100")
     { string a[] = {"NAS100","NDX","NDX100","USTEC","US100","NAS100Cash"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "US30" || base == "DJ30" || base == "DOW" || base == "WS30")
     { string a[] = {"US30","DJ30","DOW30","WS30","DOWJones30","US30Cash"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "UK100" || base == "FTSE" || base == "FTSE100")
     { string a[] = {"UK100","FTSE100","FTSE","UK100Cash"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "JPN225" || base == "NIK225" || base == "NIKKEI" || base == "JP225")
     { string a[] = {"JPN225","NIK225","NIKKEI","JP225","JPN225Cash"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "FRA40" || base == "CAC40" || base == "CAC")
     { string a[] = {"FRA40","CAC40","CAC"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "EU50" || base == "STOXX50")
     { string a[] = {"EU50","STOXX50","EUSTX50"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "ESP35" || base == "IBEX35")
     { string a[] = {"ESP35","IBEX35","SPA35"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "XAUUSD" || base == "GOLD")
     { string a[] = {"XAUUSD","GOLD","XAU/USD"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "XAGUSD" || base == "SILVER")
     { string a[] = {"XAGUSD","SILVER","XAG/USD"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "USOIL" || base == "WTI" || base == "XTIUSD")
     { string a[] = {"USOIL","WTI","XTIUSD","CL","CRUDEOIL","USOIL.cash"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }
   else if(base == "UKOIL" || base == "BRENT" || base == "XBRUSD")
     { string a[] = {"UKOIL","BRENT","XBRUSD","UKOIL.cash"};
       for(int k=0;k<ArraySize(a);k++){ArrayResize(aliases,ArraySize(aliases)+1);aliases[ArraySize(aliases)-1]=a[k];} }

   //--- Try each alias, with suffix first
   for(int i = 0; i < ArraySize(aliases); i++)
     {
      if(StringLen(sfx) > 0)
        { ArrayResize(alts, ArraySize(alts) + 1); alts[ArraySize(alts) - 1] = aliases[i] + sfx; }
      ArrayResize(alts, ArraySize(alts) + 1); alts[ArraySize(alts) - 1] = aliases[i];
     }

   //--- Attempt to select each candidate
   for(int i = 0; i < ArraySize(alts); i++)
     {
      if(SymbolSelect(alts[i], true) && SymbolInfoInteger(alts[i], SYMBOL_SELECT))
         return alts[i];
     }

   //--- Last resort: scan full Market Watch for a symbol starting with base
   int total = SymbolsTotal(false);
   for(int i = 0; i < total; i++)
     {
      string sym = SymbolName(i, false);
      if(StringFind(sym, base) == 0)
        {
         if(SymbolSelect(sym, true)) return sym;
        }
     }
   return "";
  }

void BuildSymbols()
  {
   //--- FX presets
   string m[] = {"EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD"};
   string c[] = {"EURJPY","GBPJPY","EURGBP","AUDJPY","CADJPY","EURAUD","EURCAD","GBPAUD","GBPCAD","GBPCHF","CHFJPY","NZDJPY"};
   string j[] = {"USDJPY","EURJPY","GBPJPY","AUDJPY","CADJPY","CHFJPY","NZDJPY"};
   string e[] = {"EURUSD","EURJPY","EURGBP","EURAUD","EURCAD"};
   string g[] = {"GBPUSD","GBPJPY","EURGBP","GBPAUD","GBPCAD","GBPCHF"};
   string t[] = {"EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD"};

   //--- v4.5: multi-asset presets
   string idx_eu[]  = {"DE40","UK100","FRA40","EU50","ESP35"};
   string idx_us[]  = {"US500","NAS100","US30"};
   string idx_all[] = {"DE40","UK100","FRA40","EU50","US500","NAS100","US30","JPN225"};
   string metals[]  = {"XAUUSD","XAGUSD"};
   string energy[]  = {"USOIL","UKOIL"};
   string multi[]   = {"EURUSD","GBPUSD","USDJPY","XAUUSD","DE40","US500","NAS100","USOIL"};

   string cands[]; int n = 0;
   if(InpPreset == PRESET_MANUAL || StringLen(InpCustom) > 0)
     { string p[]; int cn = StringSplit(InpCustom, ',', p);
       for(int i = 0; i < cn; i++) { StringTrimLeft(p[i]); StringTrimRight(p[i]);
         if(StringLen(p[i]) > 0) { ArrayResize(cands, n + 1); cands[n++] = p[i]; }}
       if(n == 0) { ArrayResize(cands, 1); cands[0] = _Symbol; n = 1; } }
   else if(InpPreset == PRESET_GRAFICO) { ArrayResize(cands, 1); cands[0] = _Symbol; n = 1; }
   else { switch(InpPreset) {
     case PRESET_MAJORS:       AA(cands, n, m); break;
     case PRESET_CROSSES:      AA(cands, n, c); break;
     case PRESET_JPY:          AA(cands, n, j); break;
     case PRESET_EUR:          AA(cands, n, e); break;
     case PRESET_GBP:          AA(cands, n, g); break;
     case PRESET_TOP5:         AA(cands, n, t); break;
     case PRESET_CSI:          AA(cands, n, m); AA(cands, n, c); break;
     case PRESET_CSI_MAJORS:   AA(cands, n, m); break;
     case PRESET_INDICES_EU:   AA(cands, n, idx_eu); break;
     case PRESET_INDICES_US:   AA(cands, n, idx_us); break;
     case PRESET_INDICES_ALL:  AA(cands, n, idx_all); break;
     case PRESET_METALES:      AA(cands, n, metals); break;
     case PRESET_ENERGIA:      AA(cands, n, energy); break;
     case PRESET_MULTIASSET:   AA(cands, n, multi); break;
     default: AA(cands, n, m); AA(cands, n, c); break; }}

   //--- Detect broker suffix by scanning Market Watch for EURUSD variants (more robust than trusting _Symbol length)
   string sfx = "";
   int totalMW = SymbolsTotal(false);
   for(int i = 0; i < totalMW; i++)
     {
      string sn = SymbolName(i, false);
      if(StringFind(sn, "EURUSD") == 0 && StringLen(sn) > 6)
        { sfx = StringSubstr(sn, 6); break; }
     }
   //--- Fallback: if chart symbol is clearly FX with suffix, use that
   if(StringLen(sfx) == 0 && StringLen(_Symbol) > 6)
     {
      string core_chart = StripSuffix(_Symbol);
      if(StringLen(core_chart) == 6 && DetectAssetClass(_Symbol) == CLASS_FX)
         sfx = StringSubstr(_Symbol, 6);
     }

   if(InpVerbose)
      Print("[BuildSymbols] Broker suffix detected: '", sfx, "' | ", n, " candidatos");

   ArrayResize(g_names, 0); g_cnt = 0;
   int idx_found = 0, mtl_found = 0, oil_found = 0, fx_found = 0, failed = 0;

   for(int i = 0; i < n; i++)
     {
      string sym_req = cands[i];
      ENUM_ASSET_CLASS expected = DetectAssetClass(sym_req);

      //--- For non-FX, use alias resolver (handles GER40/DE40, USOIL/WTI, etc.)
      string final_sym = "";
      if(expected != CLASS_FX)
        {
         final_sym = ResolveSymbolAlias(sym_req, sfx);
        }
      else
        {
         //--- FX: try suffix first, then plain, then scan
         if(StringLen(sfx) > 0)
           {
            string alt = sym_req + sfx;
            if(SymbolSelect(alt, true) && SymbolInfoInteger(alt, SYMBOL_SELECT))
               final_sym = alt;
           }
         if(final_sym == "")
           {
            if(SymbolSelect(sym_req, true) && SymbolInfoInteger(sym_req, SYMBOL_SELECT))
               final_sym = sym_req;
           }
         if(final_sym == "")
           {
            //--- Scan Market Watch for prefix match
            for(int k = 0; k < totalMW; k++)
              {
               string sn = SymbolName(k, false);
               if(StringFind(sn, sym_req) == 0)
                 { if(SymbolSelect(sn, true)) { final_sym = sn; break; } }
              }
           }
        }

      if(final_sym == "")
        {
         if(InpVerbose) Print("[BuildSymbols] ✗ No encontrado: ", sym_req, " (clase esperada: ", AssetClassName(expected), ")");
         failed++;
         continue;
        }

      //--- Deduplication
      bool dup = false;
      for(int jj = 0; jj < g_cnt; jj++) if(g_names[jj] == final_sym) { dup = true; break; }
      if(dup) continue;

      ArrayResize(g_names, g_cnt + 1); g_names[g_cnt++] = final_sym;
      ENUM_ASSET_CLASS ac = DetectAssetClass(final_sym);
      switch(ac)
        {
         case CLASS_FX:     fx_found++; break;
         case CLASS_INDEX:  idx_found++; break;
         case CLASS_METAL:  mtl_found++; break;
         case CLASS_ENERGY: oil_found++; break;
        }
      if(InpVerbose)
         Print("[BuildSymbols] ✓ ", sym_req, " → ", final_sym, " [", AssetClassName(ac), "]");
     }

   if(InpVerbose)
      Print("[BuildSymbols] Resumen → FX:", fx_found, " IDX:", idx_found,
            " MTL:", mtl_found, " OIL:", oil_found, " | Fallos:", failed, " | Total: ", g_cnt);
  }

void AA(string &d[], int &n, const string &s[])
  { for(int i = 0; i < ArraySize(s); i++) { ArrayResize(d, n + 1); d[n++] = s[i]; } }

void CacheSym(int i)
  { string s = g_sym[i].symbol = g_names[i];
    g_sym[i].point = SymbolInfoDouble(s, SYMBOL_POINT);
    g_sym[i].digits = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
    g_sym[i].asset_class = DetectAssetClass(s);
    g_sym[i].pip = ComputePipForClass(s, g_sym[i].asset_class, g_sym[i].point, g_sym[i].digits);
    g_sym[i].min_lot = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
    g_sym[i].max_lot = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
    g_sym[i].lot_step = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP); }

void ResetSym(int i)
  { for(int s = 0; s < SESS_MAX; s++)
      for(int t = 0; t < 2; t++)
        { int k = s*2+t;
          g_sym[i].rng_high[k] = 0; g_sym[i].rng_low[k] = 0;
          g_sym[i].rng_defined[k] = false; g_sym[i].rng_traded[k] = false; g_sym[i].rng_time[k] = 0;
          g_sym[i].fk_dir[k] = 0; g_sym[i].fk_extreme[k] = 0; g_sym[i].fk_done[k] = false; }
    g_sym[i].trades_today = 0; g_sym[i].csi_traded = false; }

void PreloadData()
  { MqlRates d[]; for(int i = 0; i < g_cnt; i++) CopyRates(g_names[i], PERIOD_M15, 0, 2000, d); }

void DetectGMT()
  { if(InpGMT == GMT_MANUAL) { g_gmt_off = InpGMTOff * 3600; return; }
    int raw = (int)(TimeCurrent() - TimeGMT());
    g_gmt_off = (int)(MathRound((double)raw / 1800.0) * 1800);
    if(g_gmt_off < -43200 || g_gmt_off > 50400) g_gmt_off = 7200; }

void CalcSessionTimes()
  { int off = g_gmt_off / 60;
    g_start_min[SESS_NY]    = Wrap(InpNY_H * 60 + InpNY_M + off);
    g_end_min[SESS_NY]      = Wrap(InpNY_End * 60 + off);
    g_start_min[SESS_LDN]   = Wrap(InpLDN_H * 60 + InpLDN_M + off);
    g_end_min[SESS_LDN]     = Wrap(InpLDN_End * 60 + off);
    g_start_min[SESS_ASIAN] = Wrap(InpASN_H * 60 + InpASN_M + off);
    g_end_min[SESS_ASIAN]   = Wrap(InpASN_End * 60 + off); }

int Wrap(int m) { if(m < 0) return m + 1440; if(m >= 1440) return m - 1440; return m; }

void TryAllRanges()
  { for(int i = 0; i < g_cnt; i++)
      for(int s = 0; s < SESS_MAX; s++)
        { if(!IsSessionEnabled(s)) continue;
          if(InpTF == ORB_M15 || InpTF == ORB_AMBOS) if(!g_sym[i].rng_defined[s*2+0]) DefRange(i, PERIOD_M15, s);
          if(InpTF == ORB_M30 || InpTF == ORB_AMBOS) if(!g_sym[i].rng_defined[s*2+1]) DefRange(i, PERIOD_M30, s); } }

datetime DayStart() { return StringToTime(TimeToString(TimeCurrent(), TIME_DATE)); }
datetime GetSessionEnd(int sess) { return g_today + (datetime)(g_end_min[sess] * 60); }

//--- v4.6: Global daily cap helpers
bool HasPairTradedToday(string sym)
  {
   for(int i = 0; i < g_pairs_traded_today_cnt; i++)
      if(g_pairs_traded_today[i] == sym) return true;
   return false;
  }

//--- Check global daily caps. Call BEFORE initiating any trade.
//    Returns true if trade is allowed, false if blocked by cap.
bool CanInitiateTrade(string sym)
  {
   // Cap 1: Max trades per day (total across all symbols)
   if(g_trades_today_total >= InpMaxTradesDia)
     {
      if(InpVerbose)
         Print("✗ CAP | ", sym, " bloqueado: límite diario alcanzado (",
               IntegerToString(g_trades_today_total), "/", IntegerToString(InpMaxTradesDia),
               " trades hoy)");
      return false;
     }
   // Cap 2: Max distinct pairs per day
   // Only blocks if this is a NEW pair and we've already hit the pair limit
   if(!HasPairTradedToday(sym) && g_pairs_traded_today_cnt >= InpMaxParesDia)
     {
      if(InpVerbose)
         Print("✗ CAP | ", sym, " bloqueado: ya operaron ",
               IntegerToString(g_pairs_traded_today_cnt), "/", IntegerToString(InpMaxParesDia),
               " pares hoy (este sería el ", IntegerToString(g_pairs_traded_today_cnt + 1), "º)");
      return false;
     }
   return true;
  }

//--- Register a trade initiation. Call AFTER a trade has been successfully opened.
void RegisterTradeInitiated(string sym)
  {
   g_trades_today_total++;
   if(!HasPairTradedToday(sym))
     {
      ArrayResize(g_pairs_traded_today, g_pairs_traded_today_cnt + 1);
      g_pairs_traded_today[g_pairs_traded_today_cnt++] = sym;
     }
   if(InpVerbose)
      Print("► CAP | ", sym, " trade #", IntegerToString(g_trades_today_total),
            "/", IntegerToString(InpMaxTradesDia),
            " | pares hoy: ", IntegerToString(g_pairs_traded_today_cnt),
            "/", IntegerToString(InpMaxParesDia));
  }

int CountOpen()
  { int c = 0; for(int i = PositionsTotal()-1; i >= 0; i--) if(g_pos.SelectByIndex(i) && g_pos.Magic() == InpMagic) c++; return c; }

int CountPending()
  { int c = 0; for(int i = OrdersTotal()-1; i >= 0; i--) { ulong t = OrderGetTicket(i); if(t > 0 && OrderGetInteger(ORDER_MAGIC) == InpMagic) c++; } return c; }

int CountOpenSym(string sym)
  { int c = 0; for(int i = PositionsTotal()-1; i >= 0; i--)
      if(g_pos.SelectByIndex(i) && g_pos.Magic() == InpMagic && g_pos.Symbol() == sym) c++;
    return c; }

double GetPipForSym(string sym)
  { for(int i = 0; i < g_cnt; i++) if(g_sym[i].symbol == sym) return g_sym[i].pip;
    // Fallback: compute asset-class-aware pip for symbols not in cache
    double pt = SymbolInfoDouble(sym, SYMBOL_POINT);
    int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
    ENUM_ASSET_CLASS ac = DetectAssetClass(sym);
    return ComputePipForClass(sym, ac, pt, dg); }

double CalcDailyClosedPnL()
  { datetime ds = DayStart(); if(!HistorySelect(ds, TimeCurrent())) return 0;
    double total = 0; int deals = HistoryDealsTotal();
    for(int i = 0; i < deals; i++)
      { ulong tk = HistoryDealGetTicket(i); if(tk == 0) continue;
        if(HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
        long en = HistoryDealGetInteger(tk, DEAL_ENTRY);
        if(en != DEAL_ENTRY_OUT && en != DEAL_ENTRY_INOUT) continue;
        total += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_COMMISSION); }
    return total; }

double CalcFloatingPnL()
  { double total = 0;
    for(int i = PositionsTotal()-1; i >= 0; i--)
      { if(!g_pos.SelectByIndex(i)) continue; if(g_pos.Magic() != InpMagic) continue;
        total += g_pos.Profit() + g_pos.Swap() + g_pos.Commission(); }
    return total; }

double RiskLot(string s, double sl, double rp)
  { double b = AccountInfoDouble(ACCOUNT_BALANCE) * rp / 100.0;
    double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE);
    double ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
    if(tv <= 0 || ts <= 0 || sl <= 0) return SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
    return b / ((sl / ts) * tv); }

double NormLot(double lot, int idx)
  { double mn = g_sym[idx].min_lot, mx = g_sym[idx].max_lot, st = g_sym[idx].lot_step;
    if(lot < mn) lot = mn; if(lot > mx) lot = mx;
    if(st > 0) lot = MathFloor(lot / st) * st;
    return NormalizeDouble(lot, 2); }

string Fm(int m) { return (m < 10) ? "0" + IntegerToString(m) : IntegerToString(m); }

void OnChartEvent(const int id, const long &lp, const double &dp, const string &sp) {}
//+------------------------------------------------------------------+
