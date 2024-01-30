# Schraubenbemessungsprogramm: Webapp mit Streamlit - Axial- und Schertragfähigkeit von Würth Vollgewindeschrauben
# Bibliotheken
from math import pi, sqrt, cos, sin
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from würth_screws_functions import get_length, ec5_87_tragfähigkeit_vg, get_min_distances_axial, get_min_distances_shear

# HTML Einstellungen
st.set_page_config(page_title="Timber Screw Designer", page_icon="🧊", layout="wide", theme="light")
st.markdown("""<style>
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;}
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {width: 500px;margin-left: -500px;}
footer:after{
    content:"Berliner Hochschule für Technik (BHT) | Konstruktiver Hoch- und Ingenieurbau (M.Eng.) | \
    Ingenieurholzbau | Prof. Dr. Jens Kickler | Cal Mense 914553";
    display:block;
    position:relative;
    color:grey;
}
</style>""",unsafe_allow_html=True)

st.markdown('''
<style>
.katex-html {
    text-align: left;
}
</style>''',
unsafe_allow_html=True
)

# Eingangsparameter
# Listen
L_kled = ['permanent', 'long-term', 'medium-term', 'short-term', 'instantaneous']
L_kmod = [[0.6, 0.7, 0.8, 0.9, 1.1], [
    0.6, 0.7, 0.8, 0.9, 1.1], [0.5, 0.55, 0.65, 0.7, 0.9]]
L_timber = ["Glulam", "Solid Wood"]
L_rho_k = [[380, 350, 410, 380, 430, 410, 450, 430], 
           [310, 350, 380, 400, 420]]
L_grade = [['GL24h', 'GL24c', 'GL28h','GL28c', 'GL32h', 'GL32c', 'GL36h', 'GL36c'],
          ['C16', 'C24', 'C30','C35', 'C40']]
L_di_axial = [[], [], [], []]
L_di_scher = [[], [], [], []]
L_no = [[], [], [], []]
L_d = [6, 8, 10, 12]

# Text
# st.image('image_header_vg.png')
original_title = '<p style="font-family:Times; color:rgb(230, 30, 40); font-size: 60px;">Timber Screw Designer</p>'
st.markdown(original_title, unsafe_allow_html=True)

#st.title('Bemessung von Vollgewindeschrauben')
st.subheader('Würth ASSY plus VG')
st.caption('DIN EN 1995-1-1 Ch. 8 & ETA-11/0190')
st.write('This program determines the load-bearing capacities of fully threaded screws with regard to axial and shear loads. \
         The manufacturer-specific characteristic values refer to a Würth ASSY plus VG as a countersunk head version. \
         The program bears no responsibility for any errors. It is advised to verify the results according to the Würth tables.')

# Eingabewerte
with st.sidebar:

    st.write("")
    st.write("")
    st.write("")
    original_title = '<p style="font-family:Times; color:rgb(0, 0, 0); font-size: 40px;">Input Parameters</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    st.latex(r"\textbf{Load Parameters}")
    st.caption("DIN EN 1995-1-1: Ch. 2.4.1 Design value of material property ")
    nkl = st.selectbox('Service Classes', [1, 2, 3])
    kled = st.selectbox('Load-Duration Classes ', L_kled)
    index = L_kled.index(kled)

    k_mod = L_kmod[nkl][index]
    gamma = 1.3
    chi = k_mod/gamma
    hersteller = 'Würth'
    st.latex('k_{mod} / \gamma = ' + str("{:.2f}".format(chi)) )

    st.latex(r"\textbf{Material Parameters}")
    st.caption("DIN EN 14080:2013 and DIN 1052:2008")
    timber = st.selectbox('Timber', L_timber)
    indexTimber = L_timber.index(timber)
    grade = st.selectbox('Grade', L_grade[indexTimber])
    verbindungsart = st.selectbox('Type of connection', ["Timber-Timber", "Steel-Timber"])

    index = L_grade[indexTimber].index(grade)  # Rohdichte des Holzes (Index)
    rho_k = L_rho_k[indexTimber][index]  # Rohdichte des Holzes

    st.latex(r"\textbf{Design Loading}")
    F_td = int(st.text_input('Axial Load', 0))
    F_vd = int(st.text_input('Shear Load', 0))

#__________________________________________________
#__________Main___________________________________
#__________________________________________________

# Image
if verbindungsart == "Timber-Timber":
    st.image('image_holz_holz.png') 
else: st.image('image_stahl_holz.png') 

# Screw Parameters
st.latex(r"\textbf{Screw Parameters}")

col1, col2, col3 = st.columns(3, gap="small")
with col1:
    d = st.selectbox('Diameter [mm]', [6,8,10,12])
    L_L, L_Li = get_length(hersteller, d)  # Liste der Längen
with col2:
    L = st.selectbox('Length [mm]', L_Li)

# Geometry Parameters
st.latex(r"\textbf{Geometry Parameters}")

col1, col2, col3 = st.columns(3, gap="small")
if verbindungsart == "Timber-Timber":
    with col1:
        t_1 = int(st.text_input('Side Wood t1 [mm]', 50))
    with col2:
        t_2 = int(st.text_input('Side Wood t2 [mm]', 100))
        t_Blech = 0
elif verbindungsart == "Steel-Timber": 
    with col1:
        t_Blech = int(st.text_input('Steel [mm]', 2))
    with col2:
        t_1 = int(st.text_input('Side Wood 1 [mm]', 50))
        t_2 = 0
#with col3:
    #width = int(st.text_input('Beam Width [mm]', 100))
#with col4:
    #height = int(st.text_input('Beam Height [mm]', 400))

col1, col2, col3 = st.columns(3, gap="small")
with col1:
    if verbindungsart == "Timber-Timber":
        alpha_1 = int(st.text_input('Angle between screw axis and fiber direction 1', 90))
    else:
        alpha_1 = st.text_input('Angle between screw axis and fiber direction 1', "N/A")
with col2:
    alpha_2 = int(st.text_input('Angle between screw axis and fiber direction 2', 0))

col1, col2, col3 = st.columns(3, gap="small")
with col1:
    n_par = int(st.text_input('Number of screws parallel to grain', 1))
with col2:
    n_perp = int(st.text_input('Number of screws perpendicular to grain', 1))

#__________________________________________________
#__________Axial___________________________________
#__________________________________________________
    
st.latex(r"\textbf{Calculation}")
with st.expander("Axial Load Capacity"):

    F_axRk1, F_vRk1, nw, l_ef = ec5_87_tragfähigkeit_vg('Würth', d, L, t_1, t_2, t_Blech, rho_k, alpha_2)
    F_axRd1 = F_axRk1*chi
    n_total = n_par*n_perp
    n_efaxial = max(n_total**0.9,n_total*0.9)
    F_axRd1tot = F_axRd1*n_efaxial
    eta_axial = F_td/F_axRd1tot
    # Umrechnung in Bogenmaß
    alph = alpha_2 * pi / 180

    a_1, a_2, a_1cg, a_2cg = get_min_distances_axial(d)

    st.latex(r"\textbf{Strengths}")
    st.caption("DIN EN 1995-1-1: Ch. 8.7.2 Axially loaded screws")
    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:   
        st.write(r"Characteristic")
        st.latex('F_{axRk} = ' + str(F_axRk1) + " kN")
    with col2: 
        st.write(r"Design")
        st.latex('F_{axRd} = ' + str("{:.2f}".format(F_axRd1)) + " kN")
    if n_efaxial > 1:
        with col3:
            st.write(r"Effective Number")
            st.latex('n_{ef} = ' + str("{:.2f}".format(n_efaxial)))
        with col4: 
            st.write(r"Design Total")
            st.latex('F_{axRdtot} = ' + str("{:.2f}".format(F_axRd1tot)) + " kN")

    col1, col2, col3, col4 = st.columns(4, gap="small")
    if F_td > 0:   
        if eta_axial < 1:
            with col1:
                st.latex(r"\textbf{Check}")
                st.progress(eta_axial, text="η = " + str(int(eta_axial*100)) + "%")
        else:
            with col1:
                st.latex(r"\textbf{Check}")
                st.error("The check is failed.")
    
    st.write("")
    st.latex(r"\textbf{Minimum Spacings and Edge Distances}")
    st.caption("DIN EN 1995-1-1: Tab. 8.6 Minimum spacings and end and edge distances for axially loaded screws")

    if st.radio("Show Minimum Spacings?", ["Don't Show","Show"]) == "Show":
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:   
            st.write(r"Parallel to grain")
            st.latex('a_{1} = ' + str(a_1) + " mm")
        with col2: 
            st.write(r"Perpendicular to grain")
            st.latex('a_{2} = ' + str(a_2) + " mm")
        with col3: 
            st.write(r"End Distance")
            st.latex('a_{1cg} = ' + str(a_1cg) + " mm")
        with col4: 
            st.write(r"Edge Distance")
            st.latex('a_{2cg} = ' + str(a_2cg) + " mm")

        st.caption("")
        st.caption("DIN EN 1995-1-1: Fig. 8.11.a - Spacings and end and edge distances ")
        st.image("image_distances_axial.png")

#__________________________________________________
#__________Shear___________________________________
#__________________________________________________
        
with st.expander("Shear Load Capacity"):

    F_axRk2, F_vRk2, nw, l_ef = ec5_87_tragfähigkeit_vg('Würth', d, L, t_1, t_2, t_Blech, rho_k, alpha_2)
    F_vRd2 = F_vRk2*chi

    # Mindestabstände
    a_1, a_2, a_3t, a_3c, a_4t, a_4c = get_min_distances_shear(d, rho_k, alpha_2)
    if a_1 >= 14*d:
        k_ef = 1
    elif a_1 >= 10*d:
        k_ef = 0.85
    elif a_1 >= 7*d:
        k_ef = 0.7
    n_efpar = n_par**k_ef
    n_efshear = n_perp * n_efpar
    F_vRd2tot = n_efshear*F_vRd2
    eta_shear = F_vd/F_vRd2tot
  
    st.latex(r"\textbf{Strengths}")
    st.caption("DIN EN 1995-1-1: Ch. 8.2 Lateral load-carrying capacity of metal dowel-type fasteners")
    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:   
        st.write(r"Characteristic")
        st.latex('F_{vRk} = ' + str(F_vRk2) + " kN")
    with col2: 
        st.write(r"Design")
        st.latex('F_{vRd1} = ' + str("{:.2f}".format(F_vRd2)) + " kN")
    if n_efshear > 1:
        with col3:
            st.write(r"Effective Number")
            st.latex('n_{ef} = ' + str("{:.2f}".format(n_efshear)))
        with col4: 
            st.write(r"Design Total")
            st.latex('F_{axRdtot} = ' + str("{:.2f}".format(F_vRd2tot)) + " kN")
        
    col1, col2, col3, col4 = st.columns(4, gap="small")
    if F_vd > 0:   
        if eta_shear < 1:
            with col1:
                st.latex(r"\textbf{Check}")
                st.progress(eta_shear, text="η = " + str(int(eta_shear*100)) + "%")
        else:
            with col1:
                st.latex(r"\textbf{Check}")
                st.error("The check is failed.")

    st.write("")
    st.latex(r"\textbf{Minimum Spacings and Edge Distances}")
    st.caption("DIN EN 1995-1-1: Tab. 8.2 - Spacings and end and edge distances")
    
    if st.radio("Show Minimum Spacings? ", ["Don't Show","Show"]) == "Show":
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:   
            st.write(r"Parallel to grain")
            st.latex('a_{1} = ' + str(a_1) + " mm")
        with col2: 
            st.write(r"Perpendicular to grain")
            st.latex('a_{2} = ' + str(a_2) + " mm")

        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1: 
            st.write(r"Distance to laoded end")
            st.latex('a_{3t} = ' + str(a_3t) + " mm")
        with col2: 
            st.write(r"Distance to unlaoded end")
            st.latex('a_{3c} = ' + str(a_3c) + " mm")
        with col3:   
            st.write(r"Distance to laoded edge")
            st.latex('a_{4t} = ' + str(a_4t) + " mm")
        with col4: 
            st.write(r"Distance to unlaoded edge")
            st.latex('a_{4c} = ' + str(a_4c) + " mm")
        
        st.caption("")
        st.caption("DIN EN 1995-1-1: Fig. B.7 - Spacings and end and edge distances")
        st.image("image_distances_shear.png")

#__________________________________________________
#__________structural analysis ____________________
#__________________________________________________
    
st.latex(r"\textbf{Report}")
with st.expander("Report"):

    alph = alpha_2*pi/180
    t_2 = L-t_1
    if t_Blech != 0:
        l_ef = L-t_Blech
    elif t_Blech == 0:
        l_ef = min(L-t_1, t_1)

    # Einganswerte
    if hersteller == 'Würth':
        # WÜrth
        L_d = [6, 8, 10, 12]
        L_f_axk = [11.5, 11, 10, 10]
        L_f_tensk = [11, 20, 32, 45]
        L_d_h = [14, 22, 25.2, 29.4]
        L_f_head = [13, 13, 10, 10]

    # Index für Kennwerte
    index = L_d.index(d)
    d = L_d[index]
    d_h = L_d_h[index]
    f_head = L_f_head[index]
    f_axk = L_f_axk[index]
    f_tensk = L_f_tensk[index]
    M_yrk = round(0.15*600*d**(2.6), 2)
    f_hk = round((0.082*rho_k*d**(-0.3)), 2)
    k_axk = 0.3+(0.7*alpha_2)/45 if alpha_2 <= 45 else 1

    # Auflistung der Kennwerte und Eingangswerte
    original_title = '<p style="font-family:Arial; color:rgb(0,0,0); font-size: 25px; font-weight: bold; ">Mechanical Properties</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    st.caption('ETA-11/0190')
    col1, col2 = st.columns(2)
    with col1:
        st.latex('d_{h} = ' + str(d_h) + ' mm')
        st.latex('l_{eff} = ' + str(l_ef) + ' mm')
        st.latex(r'''\rho_{k} = ''' + str(rho_k) + ' kg/m^3')
        st.latex('k_{axk} = ' + str(k_axk))
    with col2:
        st.latex('f_{headk} = ' + str(f_head) + ' N/mm^2')
        st.latex('f_{axk} = ' + str(f_axk) + ' N/mm^2')
        st.latex('f_{tensk} = ' + str(f_tensk) + ' N/mm^2')
        st.latex('M_{yRk} = ' + str(M_yrk) + ' Nmm')

    #__________Ausziehwiderstand__________
    st.write("")
    original_title = '<p style="font-family:Arial; color:rgb(0,0,0); font-size: 25px; font-weight: bold; ">Axial Load Capacity</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    st.latex(r"\textbf{Characteristic Withdrawal Capacity}")
    # Ausziehwiderstandrr
    # Berechnung
    F_axrk1 = (k_axk*f_axk*d*l_ef) * (rho_k/350)**0.8  # N
    F_axRk1 = round(F_axrk1/1000, 2)
    # LATEX
    st.latex(
        r''' F_{axRk}  =  k_{axk} * f_{axk} * l_{ef} * \left(\frac{\rho_{k}}{350} \right)^{0.8} = ''' + str(F_axRk1) + ' kN')

    # Kopfdurchzieh
    # Berechnung
    F_headrk = f_head*(d_h)**2 * (rho_k/350)**0.8
    # F_headrk =  (k_axk*f_axk*d*4*d) * (rho_k/350)**0.8 #N
    F_headRk = round(F_headrk/1000, 2)

    # LATEX
    st.latex(r"\textbf{Characteristic Pull-through Capacity}")
    st.latex(
        r'''F_{headRk}  = f_{head} * d_{h}^2 * \left(\frac{\rho_k}{350} \right)^{0.8} = ''' + str(F_headRk) + ' kN')

    # Zugfestigkeit
    # Berechnung
    F_tRk = f_tensk
    # LATEX
    st.latex(r"\textbf{Characteristic Tensile Capacity}")
    st.latex('F_{tRk} = f_{tensk} = ' + str(F_tRk) + ' kN')

    st.latex(r"\textbf{Resulting Axial Capacity}")
    st.caption('DIN EN 1995-1-1 Abs. 8.7.2')
    if t_Blech != 0 or t_2 > 4*d:
        # if t_Blech != 0:
        F_axRk = min(F_axRk1, F_tRk)
        F_axrk = min(F_axrk1, F_tRk*1000)
        st.write('Kopfdurchziehtragfähigkeit nicht zu berücksichtigen.')
        st.latex(r'''  F_{axRk} = min( ''' + rf'''{F_axRk1}, ''' +
                    rf'''{F_tRk}) = ''' + str(F_axRk) + ' kN')

    elif t_Blech == 0 or t_2 < 4*d:
        # elif t_Blech == 0:
        F_axRk = min(F_axRk1, F_headRk, F_tRk)
        F_axrk = min(F_axrk1, F_headrk, F_tRk*1000)
        st.latex(r'''  F_{axRk} = min( ''' + rf'''{F_axRk1}, ''' +
                    rf'''{F_headRk}, ''' + rf'''{F_tRk})  = ''' + str(F_axRk) + ' kN')

    #__________Schertragfähigkeit__________
    
    # Holz-Holz
    st.write("")
    original_title = '<p style="font-family:Arial; color:rgb(0,0,0); font-size: 25px; font-weight: bold; ">Lateral Load Capacity</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    if t_Blech == 0:

        F_vk1 = round(f_hk*t_1*d, 2)
        F_vk2 = round(f_hk*t_2*d, 2)
        F_vk3 = round((f_hk*t_1*d)/2 * (sqrt(1+2*(1+t_2/t_1 +
                        (t_2/t_1)**2)+(t_2/t_1)**2)-(1+t_2/t_1))+F_axrk/4, 2)
        F_vk4 = 1.05*(f_hk*t_1*d)/(3) * \
            (sqrt(4+(12*M_yrk)/(f_hk*t_1**2*d))-1)+F_axrk/4
        F_vk5 = 1.05*(f_hk*t_2*d)/(3) * \
            (sqrt(4+(12*M_yrk)/(f_hk*t_2**2*d))-1)+F_axrk/4
        F_vk6 = 1.15*sqrt(2*M_yrk*f_hk*d)+F_axrk/4
        F_vrk = min(F_vk1, F_vk2, F_vk3, F_vk4, F_vk5, F_vk6)

        F_vRk1 = round(F_vk1/1000, 2)
        F_vRk2 = round(F_vk2/1000, 2)
        F_vRk3 = round(F_vk3/1000, 2)
        F_vRk4 = round(F_vk4/1000, 2)
        F_vRk5 = round(F_vk5/1000, 2)
        F_vRk6 = round(F_vk6/1000, 2)
        F_vRk = round(F_vrk/1000, 2)

        st.latex(r"\textbf{Single Shear}")
        st.caption('DIN EN 1995-1-1 Abs. 8.2.2 (8.6)')
        st.latex(r''' F_{vk1} = f_{hk}*t_{1}*d =  ''' +
                    str(F_vRk1) + ' kN')
        st.latex(r''' F_{vk2} = f_{hk}*t_{2}*d =  ''' +
                    str(F_vRk2) + ' kN')
        st.latex(r''' F_{vk3} = \frac{f_{hk}*t_{1}*d}{1+\beta}*\left(\sqrt{1+2\beta^2*(1+\frac{t_2}{t_1}+\left(\frac{t_2}{t_1}\right)^2)+\beta^3\left(\frac{t_2}{t_1}\right)^2} - \beta\left(1+\frac{t_2}{t_1}\right)\right) + \frac{F_{axRk}}{4} = ''' + str(F_vRk3) + ' kN')
        st.latex(r''' F_{vk4} = 1.05 * \frac{f_{hk}*t_{1}*d}{2+\beta}*\left(\sqrt{2\beta*(1+\beta)+\frac{4*\beta*(2+\beta)*M_{yRk}}{f_{hk}*d*t_{1}^2}}-\beta\right) + \frac{F_{axRk}}{4} = ''' + str(F_vRk4) + ' kN')
        st.latex(r''' F_{vk5} = 1.05 * \frac{f_{hk}*t_{2}*d}{1+2\beta}*\left(\sqrt{2\beta^2*(1+\beta)+\frac{4*\beta*(1+2\beta)*M_{yRk}}{f_{hk}*d*t_{2}^2}}-\beta\right) + \frac{F_{axRk}}{4} = ''' + str(F_vRk5) + ' kN')
        st.latex(
            r''' F_{vk6} = 1.15 * \sqrt{\frac{2\beta}{1+\beta}}*\sqrt{2*M_{yRk}*f_{hk}*d} + \frac{F_{axRk}}{4} = ''' + str(F_vRk6) + ' kN')

        st.latex(r'''  F_{vRk} = min( ''' + rf'''{F_vRk1}, ''' + rf'''{F_vRk2}, ''' + rf'''{F_vRk3}, ''' +
                    rf'''{F_vRk4}, ''' + rf'''{F_vRk5}, ''' + rf'''{F_vRk6})  = ''' + str(F_vRk) + ' kN')

    # Holz-Stahl (einschnittig)
    # dickes Stahlblech
    elif t_Blech >= d:

        F_vk1 = f_hk*t_1*d
        F_vk2 = f_hk*t_1*d*(sqrt(2+(4*M_yrk)/(f_hk*d*t_1**2))-1)+F_axrk/4
        F_vk3 = 2.3*sqrt(M_yrk*f_hk*d)+F_axrk/4
        F_vrk = min(F_vk1, F_vk2, F_vk3)

        F_vRk1 = round(F_vk1/1000, 2)
        F_vRk2 = round(F_vk2/1000, 2)
        F_vRk3 = round(F_vk3/1000, 2)
        F_vRk = round(F_vrk/1000, 2)

        st.latex(r"\textbf{Thick Plate in Single Shear}")   
        st.caption('DIN EN 1995-1-1 Abs. 8.2.3 (8.10)')
        st.latex(r''' F_{vk1} = f_{hk}*t_{1}*d =  ''' +
                    str(F_vRk1) + ' kN')
        st.latex(
            r''' F_{vk2} = f_{hk}*t_{2}*d * \left( \sqrt{2+ r( \frac{4*M_{yRk}}{f_{hk}*d*t_{1}^2}} ) \right) + \frac{F_{axRk}}{4} = ''' + str(F_vRk2) + ' kN')
        st.latex(
            r''' F_{vk3} = 2.3 * \sqrt{2*M_{yRk}*f_{hk}*d} + \frac{F_{axRk}}{4} = ''' + str(F_vRk3) + ' kN')
        st.latex(r'''  F_{vRk} = min( ''' + rf'''{F_vRk1}, ''' +
                    rf'''{F_vRk2}, ''' + rf'''{F_vRk3}) = ''' + str(F_vRk) + ' kN')

    # dünnes Stahlblech alpha
    elif t_Blech < d:

        F_vk1 = 0.4*f_hk*t_1*d
        F_vk2 = 1.15*sqrt(2*M_yrk*f_hk*d)+F_axrk/4
        F_vrk = min(F_vk1, F_vk2)

        F_vRk1 = round(F_vk1/1000, 2)
        F_vRk2 = round(F_vk2/1000, 2)
        F_vRk = round(F_vrk/1000, 2)

        st.latex(r"\textbf{Thin Plate in Single Shear}")   
        st.caption('DIN EN 1995-1-1 Abs. 8.2.3 (8.9)')
        st.latex(
            r''' F_{vk1} = 0.4 * f_{hk}*t_{1}*d =  ''' + str(F_vRk1) + ' kN')
        st.latex(
            r''' F_{vk2} = 1.15 * \sqrt{2*M_{yRk}*f_{hk}*d} + \frac{F_{axRk}}{4} = ''' + str(F_vRk2) + ' kN')
        st.latex(r'''  F_{vRk} = min( ''' + rf'''{F_vRk1}, ''' +
                    rf'''{F_vRk2}) = ''' + str(F_vRk) + ' kN')

    #__________Nachweise__________
    
    st.write("")
    original_title = '<p style="font-family:Arial; color:rgb(0,0,0); font-size: 25px; font-weight: bold; ">Check</p>'
    st.markdown(original_title, unsafe_allow_html=True)


    # Nachweisführung: Bemessungswerte
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.latex(r"\textbf{Design Axial Load Capacity}") 
        st.latex(r'''F_{axRk} = ''' + str(F_axRk) + ' kN') 
        st.latex(r'''F_{axRd} = \frac{F_{axRk}*k_{mod}}{\gamma_{m}} = ''' +
                    str(round(F_axRk*k_mod/(gamma), 2)) + ' kN')
        if n_efaxial > 1:
            st.latex(r'''n_{ef} = ''' + str(round(n_efaxial, 2)))
            st.latex(r'''F_{axRd.tot} = ''' + str(round(F_axRd1tot,2)) + ' kN') 
        if F_td != 0:
            st.latex(r'''F_{axEd} = ''' + str(round(F_td, 2)) + ' kN')
            st.latex(r'''\eta_{axd} = \frac{F_{axEd}}{F_{axRd}} = ''' +
                    str(round(F_td/(F_axRd1tot), 2)))
    with col2:
        st.latex(r"\textbf{Design Lateral Load Capacity}")  
        st.latex(r'''F_{vRk} = ''' + str(F_vRk) + ' kN')
        st.latex(r'''F_{vRd} = \frac{F_{vRk}*k_{mod}}{\gamma_{m}} = ''' +
                    str(round(F_vRk*k_mod/(gamma), 2)) + ' kN')
        if n_efshear > 1:
            st.latex(r'''n_{ef} = ''' + str(round(n_efshear, 2)))
            st.latex(r'''F_{vRd.tot} = ''' + str(round(F_vRd2tot,2)) + ' kN') 
        if F_vd != 0:
            st.latex(r'''F_{vEd} = ''' + str(round(F_vd, 2)) + ' kN')
            st.latex(r'''\eta_{vd} = \frac{F_{vEd}}{F_{vRd}} = ''' +
                        str(round(F_vd/(F_vRd2tot), 2)))

