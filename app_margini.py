import streamlit as st
import pandas as pd
import os

# Funzione per formattare i numeri con la virgola
def format_num(valore):
    return f"{valore:.2f}".replace(".", ",")

# Configurazione iniziale della pagina
st.set_page_config(page_title="Dashboard Prezzi & Margini", layout="wide", page_icon="📊")

# --- INIEZIONE CSS PER GRAFICA MODERNA ---
st.markdown("""
    <style>
        /* Stile moderno per le schede delle metriche (Card) */
        [data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.05);
            border-radius: 10px;
            padding: 15px 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
            border-top: 4px solid #1E88E5; /* COLORE PRINCIPALE: Cambia questo codice Hex per abbinarlo esattamente al tuo logo */
            transition: transform 0.2s ease-in-out;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.1);
        }
        /* Rende le scritte delle etichette più eleganti */
        [data-testid="stMetricLabel"] {
            font-weight: 600;
            font-size: 16px;
        }
        /* Nasconde lo spazio bianco in cima alla pagina */
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- INSERIMENTO LOGO (ALLINEATO A SINISTRA) ---
# Usiamo due colonne: la prima [1] è piccola per il logo, la seconda [4] è grande e vuota per spingerlo a sinistra
col_logo, col_spazio = st.columns([1, 4]) 
with col_logo:
    if os.path.exists("full_logo.jpg"):
        st.image("full_logo.jpg", use_container_width=True)
    else:
        st.warning("⚠️ Logo non trovato. Assicurati che il file si chiami 'full_logo.jpg' e sia nella stessa cartella di questa app.")

st.title("📊 Calcolatore Prezzi & Margini")
st.markdown("**Tutti i costi e ricavi si intendono al netto dell'IVA come da Contabilità, ad eccezione del prezzo di vendita (BUY BOX).**")
st.divider()

# Definizione dei Marketplace e relative aliquote IVA
marketplaces = {
    "Amazon IT 🇮🇹": 0.22,
    "Amazon DE 🇩🇪": 0.19,
    "Amazon FR 🇫🇷": 0.20,
    "Amazon ES 🇪🇸": 0.21,
    "Amazon NL 🇳🇱": 0.21
}

country_names = {
    "Amazon IT 🇮🇹": "Italia",
    "Amazon DE 🇩🇪": "Germania",
    "Amazon FR 🇫🇷": "Francia",
    "Amazon ES 🇪🇸": "Spagna",
    "Amazon NL 🇳🇱": "Paesi Bassi"
}

iva_it_acquisti = 0.22
iva_it_commissioni = 0.22

# --- SEZIONE INPUT DATI ---
st.subheader("📝 Parametri di Vendita")
selected_market = st.selectbox("🌍 Seleziona il Marketplace di Vendita:", list(marketplaces.keys()))
nome_stato = country_names[selected_market]

col1, col2, col3 = st.columns(3)

with col1:
    buy_box = st.number_input("💰 Prezzo BUY BOX (IVA Inclusa) €", min_value=0.0, value=None, step=0.10, placeholder="Inserisci Prezzo...")
    iva_rate = st.number_input("⚖️ Aliquota IVA Vendita (%)", min_value=0.0, max_value=100.0, value=marketplaces[selected_market]*100, step=1.0) / 100

with col2:
    costo_acquisto = st.number_input("🛒 Costo di Acquisto €", min_value=0.0, value=None, step=0.10, placeholder="Inserisci Costo...")
    commissioni_perc = st.selectbox(
        "📉 % Commissione Amazon (Segnalazione)", 
        options=[7.0, 15.0], 
        index=None, 
        placeholder="Seleziona la %...",
        format_func=lambda x: f"{x:.0f}".replace(".", ",")
    )

with col3:
    preset_logistica = st.selectbox(
        "📌 Seleziona Fascia Logistica FBA €", 
        options=[2.65, 3.24, 3.39, 3.64, 3.94, 3.99, 4.17], 
        index=None, 
        placeholder="Seleziona la fascia...",
        format_func=lambda x: f"{x:.2f}".replace(".", ",")
    )
    
    val_logistica = float(preset_logistica) if preset_logistica is not None else None
    costo_logistica = st.number_input("📦 Costo Logistica Effettivo €", min_value=0.0, value=val_logistica, step=0.10, placeholder="Inserisci Costo Logistica...")

st.divider()

# --- MOTORE DI CALCOLO E DASHBOARD ---
if buy_box is not None and buy_box > 0 and commissioni_perc is not None and costo_logistica is not None:
    
    commissioni_perc_val = commissioni_perc / 100
    imponibile = buy_box / (1 + iva_rate)
    iva_vendita = buy_box - imponibile
    costo_segnalazione = buy_box * commissioni_perc_val
    digital_tax = costo_segnalazione * 0.03
    
    commissioni_amz_netto = costo_logistica + costo_segnalazione + digital_tax
    iva_commissioni_amz = commissioni_amz_netto * iva_it_commissioni
    commissioni_amz_lordo = commissioni_amz_netto + iva_commissioni_amz
    
    ricavo_netto = imponibile - commissioni_amz_netto

    # DASHBOARD: RISULTATI VENDITA
    st.subheader(f"📈 Risultati Vendita su {selected_market}")
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("Imponibile Vendita", f"€ {format_num(imponibile)}")
    res_col2.metric(f"IVA Vendita ({iva_rate*100:.0f}%)", f"€ {format_num(iva_vendita)}")
    res_col3.metric("Spese Amazon Nette", f"€ {format_num(commissioni_amz_netto)}")
    res_col4.metric("Ricavo Netto", f"€ {format_num(ricavo_netto)}")
    
    # DASHBOARD: PROFITTO
    if costo_acquisto is not None and costo_acquisto > 0:
        iva_acquisto = costo_acquisto * iva_it_acquisti
        margine_contributivo = ricavo_netto - costo_acquisto
        margine_perc = (margine_contributivo / imponibile) * 100 if imponibile > 0 else 0
        roi_perc = (margine_contributivo / costo_acquisto) * 100
        mark_up = ricavo_netto / costo_acquisto

        st.subheader("🎯 Profitto e Indici")
        prof_col1, prof_col2, prof_col3, prof_col4 = st.columns(4)
        margine_color = "normal" if margine_contributivo >= 0 else "inverse"
        
        prof_col1.metric("Margine Contributivo", f"€ {format_num(margine_contributivo)}", delta_color=margine_color)
        prof_col2.metric("Margine % (su Imp.)", f"{format_num(margine_perc)} %")
        prof_col3.metric("ROI", f"{format_num(roi_perc)} %")
        prof_col4.metric("Mark-Up", f"{format_num(mark_up)}")

        # DETTAGLIO COSTI E SPESE AMAZON
        with st.expander("🔍 Clicca per espandere il Dettaglio delle Spese Amazon"):
            costi_col1, costi_col2, costi_col3, costi_col4 = st.columns(4)
            
            iva_logistica = costo_logistica * iva_it_commissioni
            iva_segnalazione = costo_segnalazione * iva_it_commissioni
            iva_digital_tax = digital_tax * iva_it_commissioni
            
            costi_col1.info(f"📦 **Logistica FBA**\n\nNetto: € {format_num(costo_logistica)}\n\nIVA (22%): € {format_num(iva_logistica)}\n\n**Lordo: € {format_num(costo_logistica + iva_logistica)}**")
            costi_col2.info(f"📉 **Segnalazione**\n\nNetto: € {format_num(costo_segnalazione)}\n\nIVA (22%): € {format_num(iva_segnalazione)}\n\n**Lordo: € {format_num(costo_segnalazione + iva_segnalazione)}**")
            costi_col3.warning(f"🏛️ **Digital Tax**\n\nNetto: € {format_num(digital_tax)}\n\nIVA (22%): € {format_num(iva_digital_tax)}\n\n**Lordo: € {format_num(digital_tax + iva_digital_tax)}**")
            costi_col4.error(f"🧾 **TOTALE AMAZON**\n\nNetto: € {format_num(commissioni_amz_netto)}\n\nIVA (22%): € {format_num(iva_commissioni_amz)}\n\n**Lordo: € {format_num(commissioni_amz_lordo)}**")

        st.divider()

        # DASHBOARD: FLUSSI IVA
        st.subheader(f"🏛️ Report Fiscale IVA ({nome_stato})")
        totale_credito_it = iva_acquisto + iva_commissioni_amz
        
        iva_col1, iva_col2, iva_col3 = st.columns(3)
        iva_col1.error(f"🔴 **IVA a Debito (Vendita):**\n\n€ {format_num(iva_vendita)}\n\n*(Da versare in {nome_stato})*")
        iva_col2.success(f"🟢 **IVA a Credito (Italia):**\n\n€ {format_num(totale_credito_it)}\n\n*(Merce: € {format_num(iva_acquisto)} + Amz: € {format_num(iva_commissioni_amz)})*")
        
        saldo_iva_it = 0
        with iva_col3:
            if nome_stato == "Italia":
                saldo_iva_it = iva_vendita - totale_credito_it
                if saldo_iva_it > 0:
                    st.warning(f"⚖️ **Saldo IVA Italia (Da Versare):**\n\n€ {format_num(saldo_iva_it)}")
                else:
                    st.info(f"⚖️ **Saldo IVA Italia (Credito):**\n\n€ {format_num(abs(saldo_iva_it))}")
            else:
                st.warning(f"⚖️ **Versamento in {nome_stato}:** € {format_num(iva_vendita)}\n\n**Credito in Italia:** € {format_num(totale_credito_it)}")

        st.divider()

        # DASHBOARD: FLUSSI DI CASSA
        st.subheader("💸 Simulazione Flussi di Cassa (C/C Bancario)")
        st.caption("Ipotesi: Sul conto hai esattamente la cifra per comprare il prodotto, incassi la vendita e paghi l'IVA dovuta.")
        
        costo_acquisto_lordo = costo_acquisto + iva_acquisto
        saldo_wallet = buy_box - commissioni_amz_lordo
        
        if nome_stato == "Italia":
            imposte_da_versare = saldo_iva_it if saldo_iva_it > 0 else 0
            credito_residuo = abs(saldo_iva_it) if saldo_iva_it <= 0 else 0
        else:
            imposte_da_versare = iva_vendita
            credito_residuo = totale_credito_it
            
        cc_finale = saldo_wallet - imposte_da_versare
        delta_cc = cc_finale - costo_acquisto_lordo
        
        cf_col1, cf_col2, cf_col3, cf_col4, cf_col5 = st.columns(5)
        
        cf_col1.metric("1. Saldo Iniziale C/C", f"€ {format_num(costo_acquisto_lordo)}")
        cf_col2.metric("2. Pagamento Merce", f"€ 0,00", delta=f"-€ {format_num(costo_acquisto_lordo)}", delta_color="inverse")
        cf_col3.metric("3. Saldo Wallet Amazon", f"€ {format_num(saldo_wallet)}")
        cf_col4.metric("4. C/C Finale (Dopo Tasse)", f"€ {format_num(cc_finale)}", delta=f"-€ {format_num(imposte_da_versare)} (Tasse)", delta_color="inverse")
        
        delta_color = "normal" if delta_cc >= 0 else "inverse"
        cf_col5.metric("5. DELTA C/C", f"€ {format_num(delta_cc)}", delta=f"€ {format_num(delta_cc)}", delta_color=delta_color)
        
        if credito_residuo > 0:
            st.info(f"💡 **Oltre al Delta C/C di € {format_num(delta_cc)}, hai un Credito IVA nel cassetto fiscale (Italia) di € {format_num(credito_residuo)}** \n\nIl tuo vero arricchimento finale è quindi € {format_num(delta_cc + credito_residuo)} (Delta + Credito), che corrisponde esattamente al tuo Margine Contributivo!")

    else:
        st.warning("⚠️ Inserisci il **Costo di Acquisto** per generare la Dashboard dei Profitti, dell'IVA e dei Flussi Bancari.")

else:
    st.info("👆 Inizia compilando i parametri di vendita qui sopra per generare la Dashboard.")
