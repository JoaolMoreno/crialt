# Estilo de Tipografia e Design para Aplicação CRIALT

Este documento define as diretrizes de tipografia e estilo para a nova aplicação da CRIALT, com base no manual da marca. O objetivo é manter uma estética moderna, limpa e profissional consistente com a marca.

## Filosofia Geral

O design deve ser minimalista, elegante e focado na legibilidade. A interface deve priorizar o conteúdo, utilizando amplos espaços em branco para criar uma experiência de usuário calma e organizada. A hierarquia visual clara é essencial, guiando o usuário de forma intuitiva através da aplicação.

---

## Paleta de Cores

A paleta de cores da marca foi definida para transmitir sua essência. As cores devem ser utilizadas para manter a padronização em todas as aplicações.

- **Cor Principal 1 (Texto e Elementos Escuros):**
    - HEX: `#35271C`
    - RGB: 53 29 28
- **Cor Principal 2 (Destaques e Acentos):**
    - HEX: `#B95830`
    - RGB: 185 48 48
- **Cor Principal 3 (Fundos Claros e Suporte):**
    - HEX: `#CDC0A6`
    - RGB: 205 192 166
- **Fundo Principal:**
    - `#FFFFFF` (Branco) — Recomenda-se o uso como cor de fundo principal para áreas de conteúdo, para manter a legibilidade e uma estética limpa.

**Observações de Uso:**
- **Uso em Telas:** As cores no formato HEX e RGB devem ser utilizadas para aplicações em dispositivos eletrônicos.
- **Uso para Impressão:** Para materiais impressos, deve-se utilizar o padrão CMYK.

---

## Tipografia

Foram estabelecidas duas fontes para a marca, que devem ser usadas em conjunto para padronizar a identidade visual.

- **Fonte para Títulos:** DIORE
- **Fonte para Textos:** MONTSERRAT

### Hierarquia Tipográfica

**Título Principal (H1)**
- Uso: Títulos de páginas principais
- Fonte: DIORE
- Tamanho: 32px
- Peso: 400 (Regular)
- Espaçamento entre letras: 1.5px
- Cor: `#35271C`

**Título de Seção (H2)**
- Uso: Títulos para seções importantes dentro de uma página
- Fonte: DIORE
- Tamanho: 24px
- Peso: 400 (Regular)
- Cor: `#35271C`

**Subtítulo (H3)**
- Uso: Títulos para cartões, itens de lista ou subsecções
- Fonte: DIORE
- Tamanho: 18px
- Peso: 600 (SemiBold)
- Cor: `#35271C`

**Corpo do Texto (Body)**
- Uso: Parágrafos e textos descritivos em geral
- Fonte: Montserrat
- Tamanho: 16px
- Peso: 400 (Regular)
- Altura da linha: 1.6
- Cor: `#35271C`

**Texto de Destaque (Emphasis/Price)**
- Uso: Valores monetários e informações importantes que precisam de destaque
- Fonte: Montserrat Bold
- Tamanho: 20px
- Peso: 700 (Bold)
- Cor: `#B95830`

**Legenda / Observação (Caption)**
- Uso: Notas de observação, textos auxiliares e metadados
- Fonte: Montserrat Italic
- Tamanho: 14px
- Peso: 400 (Regular, Itálico)
- Cor: `#35271C`

---

## Layout e Espaçamento

- **Alinhamento:** Todo o texto deve ser alinhado à esquerda por padrão para garantir a máxima legibilidade. Títulos principais podem ser centralizados em contextos específicos, como em páginas de boas-vindas.
- **Espaço em Branco:** Use margens e preenchimentos generosos para evitar uma interface congestionada. Um espaçamento base de 8px é recomendado (ex: 8px, 16px, 24px, 32px).
- **Divisores:** Para separar seções de conteúdo, utilize linhas finas e sólidas (`1px`) na cor `#CDC0A6`.

---

## Componentes Visuais

**Botões**
- Primário: Fundo sólido na cor `#35271C` com texto em `#FFFFFF`.
- Secundário: Fundo transparente com borda de `1px` sólida na cor `#35271C` e texto na cor `#35271C`.
- Botão de Destaque (Call-to-Action): Fundo sólido na cor `#B95830` com texto em `#FFFFFF`.
- Tipografia do Botão: Montserrat SemiBold, 16px, todo em maiúsculas (UPPERCASE).

**Listas**
- Listas com Marcadores: Utilize marcadores simples (círculos ou traços) para listas de itens.
- Listas Numeradas: Use para processos passo a passo.

**Imagens e Renders**
- As imagens devem ser de alta qualidade e apresentadas com destaque, ocupando áreas significativas da tela para replicar o impacto visual da proposta.

---

## Padrão de Listas, Tabelas e Paginação

### Estrutura Geral
- Utilize o container `.list-section` para envolver listas, tabelas e ações, garantindo espaçamento, fundo, borda e sombra padronizados.
- Títulos de página (h1) sempre com fonte DIORE, 32px, alinhados à esquerda.
- Ações de lista (filtros, busca, botões) agrupadas em `.list-actions`, com espaçamento horizontal e vertical consistente.
- Tabelas de dados devem usar `.list-table`, com cabeçalhos destacados, bordas suaves e células com padding generoso.
- Estados vazios devem ser exibidos com `.empty-state`, fonte Montserrat 16px, cor #666, estilo itálico e centralizado.

### Paginação
- Use o container `.pagination-controls` para os controles de navegação.
- Botões de paginação devem seguir o padrão `.btn-padrao` (Montserrat, 16px, uppercase, fundo #35271C, texto #FFFFFF, borda-radius 6px).
- O texto de página atual deve ser Montserrat, 15px, cor #35271C, peso 500.
- Espaçamento entre botões e texto: 16px.
- Em telas pequenas, os controles devem se alinhar em coluna, ocupando toda a largura disponível.

### Botões
- Botões de ação em listas usam `.list-btn` ou `.action-btn` conforme contexto.
- Ícones Material Icons sempre alinhados à esquerda do texto, tamanho 20px.
- Botões desabilitados com cor de fundo #CDC0A6 e texto #35271C, opacidade reduzida.

### Responsividade
- Em telas menores que 900px, ações e filtros devem se alinhar em coluna.
- Tabelas e controles de paginação devem ajustar padding e fonte para melhor leitura.

### Cores e Tipografia
- Seguir rigorosamente a paleta e hierarquia tipográfica já descrita.
- Elementos de destaque (valores, status) devem usar as cores de acento e estilos definidos.

---

## Exemplos de Uso

```html
<section class="list-section">
  <h1>Título da Página</h1>
  <div class="list-actions">
    <button class="list-btn"><span class="material-icons">add_circle</span> Novo</button>
    <input type="text" class="search-input" placeholder="Buscar..." />
    <select class="filter-select"><option>Filtro</option></select>
  </div>
  <table class="list-table">
    <thead>
      <tr><th>Coluna</th></tr>
    </thead>
    <tbody>
      <tr><td>Dado</td></tr>
    </tbody>
  </table>
  <div class="empty-state">Nenhum item encontrado.</div>
  <div class="pagination-controls">
    <button class="btn-padrao">Anterior</button>
    <span>Página 1 de 10</span>
    <button class="btn-padrao">Próxima</button>
  </div>
</section>
```
