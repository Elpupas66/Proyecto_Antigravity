//+------------------------------------------------------------------+
//|                                     Vortex_Patxi_IA.mq5      |
//|                    Generado para Laboratorio Antigravity        |
//+------------------------------------------------------------------+
#property copyright "Laboratorio IA"
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_plots   1

// Propiedades del gráfico
#property indicator_type1   DRAW_COLOR_HISTOGRAM
#property indicator_color1  clrDodgerBlue, clrNavy, clrGray, clrDodgerBlue
#property indicator_width1  2

// Entradas
input int    InpPeriod   = 14;    // Periodo Vortex
input double InpScale    = 100.0; // Escala multiplicadora
input double InpExtreme  = -17.0; // Nivel Extremo

// Buffers matemáticos internos
double BufferVortex[];
double BufferColors[];

//+------------------------------------------------------------------+
int OnInit()
  {
   SetIndexBuffer(0, BufferVortex, INDICATOR_DATA);
   SetIndexBuffer(1, BufferColors, INDICATOR_COLOR_INDEX);
   
   IndicatorSetDouble(INDICATOR_LEVELVALUE, 0, InpExtreme);
   IndicatorSetDouble(INDICATOR_LEVELVALUE, 1, MathAbs(InpExtreme));
   IndicatorSetDouble(INDICATOR_LEVELVALUE, 2, 0);

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
int OnCalculate(const int rates_total, const int prev_calculated, const datetime &time[], const double &open[], const double &high[], const double &low[], const double &close[], const long &tick_volume[], const long &volume[], const int &spread[])
  {
   if(rates_total < InpPeriod) return(0);

   int limit = prev_calculated == 0 ? InpPeriod : prev_calculated - 1;

   for(int i = limit; i < rates_total; i++)
     {
      double sumVMP = 0;
      double sumVMM = 0;
      double sumTR = 0;
      
      for(int j = 0; j < InpPeriod; j++)
        {
         int index = i - j;
         if(index < 1) continue;
         
         double vmp = MathAbs(high[index] - low[index-1]);
         double vmm = MathAbs(low[index] - high[index-1]);
         
         double tr1 = high[index] - low[index];
         double tr2 = MathAbs(high[index] - close[index-1]);
         double tr3 = MathAbs(low[index] - close[index-1]);
         double tr = MathMax(tr1, MathMax(tr2, tr3));
         
         sumVMP += vmp;
         sumVMM += vmm;
         sumTR += tr;
        }
      
      double vip = sumTR > 0 ? sumVMP / sumTR : 0;
      double vim = sumTR > 0 ? sumVMM / sumTR : 0;
      
      BufferVortex[i] = (vip - vim) * InpScale;
      
      // Colores
      if(BufferVortex[i] >= 0) {
         if(BufferVortex[i] > BufferVortex[i-1]) BufferColors[i] = 0; // Blue rising
         else BufferColors[i] = 1; // Navy falling
      } else {
         if(BufferVortex[i] < BufferVortex[i-1]) BufferColors[i] = 2; // Gray falling
         else BufferColors[i] = 3; // Blue rising (señal de entrada)
      }
     }
     
   return(rates_total);
  }
//+------------------------------------------------------------------+
