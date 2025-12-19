# 🚀 Otimizador de Imagens Py
- Uma aplicação desktop desenvolvida em Python para otimizar, redimensionar e converter imagens em lote de forma rápida e eficiente. Utiliza uma interface moderna (Dark Mode) e suporta processamento recursivo de subpastas.

## Funcionalidades Principais
### 1. Seleção e Leitura Inteligente
- **Processamento em Lote:** _Seleciona uma pasta raiz e o programa identifica automaticamente todas as imagens compatíveis._
- **Suporte a Subpastas:** _O sistema percorre recursivamente todas as subpastas da origem (os.walk), mantendo a estrutura de diretórios na saída._
- **Formatos Suportados:** _Detecta arquivos **.jpg, .jpeg, .png e .webp.**_
- **Listagem Visual:** _Exibe uma lista com caixas de seleção (checkboxes) para escolher exatamente quais arquivos processar._

### 2. Opções de Redimensionamento (Resize)
- Otimize o tamanho físico das imagens com três modos distintos:
  - **Manter Tamanho:** _Preserva as dimensões originais (apenas comprime)._
  - **Reduzir por Porcentagem (%):** _Opções predefinidas (10%, 25%, 50%, 75%, 90%) para redução rápida._
  - **Máximo em Pixels (Px):** Controle preciso com lógica inteligente:
    - **Largura Fixa:** _Ajusta a altura automaticamente para manter a proporção._
    - **Altura Fixa:** _Ajusta a largura automaticamente._
- **Dimensões Máximas:** _Se preencher ambos, a imagem será redimensionada para caber dentro desses limites._

### 3. Conversão e Compressão
- **Controle de Qualidade:** _Slider ajustável (10% a 100%) para definir o nível de compressão._
- **Conversão de Formato:** _Permite manter o formato original ou converter todos os arquivos para JPG, PNG ou WEBP._
- _Converte automaticamente imagens com transparência (RGBA) para RGB ao salvar em JPG._

### 4. Interface e Feedback
- **Design Moderno:** _Interface escura baseada em customtkinter._
- **Log em Tempo Real:** _Painel de texto que exibe o status de cada arquivo processado._
- **Relatório de Economia:** _Ao final, exibe o total de MBs economizados no disco._
- **Barra de Progresso:** _Visualização do andamento da otimização._

## 🛠️ Como Usar
- Execute o script.
- Clique em "Selecionar Pasta de Origem".
- Aguarde o carregamento da lista de imagens e selecione quais deseja processar (ou deixe todas marcadas).
- Configure as opções de Qualidade, Formato de Saída e Redimensionamento.
- Clique em **"INICIAR OTIMIZAÇÃO".**

**Os arquivos gerados serão salvos numa pasta chamada Otimizadas dentro do diretório de origem, preservando a estrutura original.**

## 📦 Dependências
- Para executar este projeto, é necessário instalar as seguintes bibliotecas Python:
```
pip install customtkinter pillow
```
