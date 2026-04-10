# Color Match

## Orientações para rodar o projeto

### 1. Crie o ambiente virtual na raiz do projeto:

```powershell
python -m venv venv
```

### 2. Ative o ambiente virtual:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Instale as dependências pelo arquivo `requirements.txt`:

```powershell
pip install -r requirements.txt
```

### 4. Para rodar basta entrar no terminal da raiz do projeto:

```powershell
uvicorn app:app --reload
```
---

# Metodologia e Tecnologias Utilizadas

Este projeto utiliza técnicas de processamento de imagem, visão computacional e análise cromática para identificar características faciais e gerar uma paleta de cores personalizada.

---

## Captura e Pré-processamento

- Utilizamos algoritmo de captura de tela para obtenção da imagem do usuário.
- Aplicamos **filtragem gaussiana** com máscara **5x5** e desvio padrão calculado automaticamente pelo OpenCV.
- Essa etapa reduz ruídos de alta frequência antes da detecção facial.

---

## Detecção Facial

- Utilizamos o método `get_frontal_face_detector()` para localizar o rosto.
- O detector é baseado em **HOG + SVM**.
- Para mapear os pontos faciais, utilizamos o modelo `shape_predictor_68_face_landmarks.dat`.
- Esse modelo identifica **68 pontos anatômicos** do rosto, incluindo olhos, sobrancelhas, nariz, boca e contorno facial.

---

## Extração de Regiões Faciais

- Utilizamos **operadores morfológicos** durante a extração das regiões faciais.
- Essa etapa é realizada em `deteccao_facial.py` / `extract_face_part`.

---

## Segmentação por Cor

- Em `color_extract.py`, cada região é convertida para **HSV**.
- Aplicamos um **range de cor de pele** para segmentar apenas os pixels desejados.

---

## Extração de Cores Dominantes

- Aplicamos **K-Means** com **k = 4** nos pixels segmentados.
- Utilizamos histograma para identificar a frequência de cada cluster.
- Filtramos pixels:
  - Pretos `(0,0,0)`
  - Azuis `(255,0,0)`
- Retornamos a cor dominante de cada região facial.

---

## Conversão de Espaço de Cor

- Em `cores_pessoais.py`, convertemos as cores dominantes de **sRGB** para:
  - **Lab (CIE L*a*b*)**
  - **HSV**

---

## Classificação Cromática

- Em `analise_tom.py`, utilizamos o canal **b do Lab** para definir temperatura:
  - **b positivo:** quente
  - **b negativo:** frio
- Aplicamos pesos:
  - Pele: **30**
  - Sobrancelha: **20**
  - Olhos: **5**

### Subtom

- Se quente: compara entre **Primavera** e **Outono**
- Se frio: compara entre **Verão** e **Inverno**

---

## Geração de Paleta

- Em `recomendacao_cores.py`, geramos uma imagem **600x600**.
- Criamos uma roda de cores com **20 fatias**.
- A foto do usuário é recortada em círculo e inserida no centro da paleta.

---

## Métrica de Qualidade (Opcional)

- Em `check_cores.py`, caso seja enviado um color checker:
  - Dividimos a imagem em grid **4x6**
  - Extraímos a cor média de cada patch
  - Calculamos **Delta E CIE76**
  - Comparamos com os valores do **X-Rite ColorChecker Classic**

