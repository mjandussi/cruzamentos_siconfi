# Segurança

## Como relatar uma vulnerabilidade

O projeto ainda não registra neste repositório um canal privado de divulgação
responsável. Essa configuração é uma **pendência do mantenedor**.

Enquanto o canal privado não for publicado:

- não abra uma issue contendo credenciais, dados de sessão, instruções de
  exploração ou outra informação sensível;
- use uma [issue pública](https://github.com/mjandussi/cruzamentos_siconfi/issues)
  apenas para informar, sem detalhes exploráveis, que deseja contato privado;
- inclua detalhes técnicos somente depois que o mantenedor indicar um meio
  privado.

Uma política formal de versões suportadas e prazo de resposta também ainda não
foi definida. Não presuma suporte de segurança para cópias antigas do projeto.

## Modelo de segurança atual

O aplicativo foi projetado como uma ferramenta Streamlit simples. Por padrão,
`AUTH_ENABLED=false` e não há tela de login obrigatória.

Quando a autenticação é habilitada:

- as senhas são comparadas com hashes bcrypt definidos em `.env`;
- a sessão e as tentativas de login ficam em `st.session_state`;
- o tempo de sessão, o número de tentativas e o bloqueio são configuráveis;
- não existe banco de usuários, log central de autenticação, bloqueio global
  por conta, segundo fator ou integração com um provedor de identidade.

O bloqueio de tentativas é local à sessão do Streamlit e pode ser perdido com
uma nova sessão ou reinício. Ele reduz erros repetidos na mesma sessão, mas não
deve ser apresentado como proteção completa contra força bruta.

## Recomendações para publicação

Para disponibilizar o aplicativo fora de uma máquina local:

1. termine o tráfego em HTTPS;
2. considere colocar autenticação, limitação de requisições e logs no proxy
   reverso ou em um provedor de identidade confiável;
3. execute o processo com um usuário sem privilégios e acesso mínimo ao sistema
   de arquivos;
4. mantenha Python e dependências atualizados e revise as versões antes do
   deploy;
5. limite tamanho de upload, memória e tempo de requisição conforme a
   infraestrutura;
6. não exponha arquivos de desenvolvimento, ambientes virtuais ou o `.env` no
   servidor web;
7. faça uma verificação manual do fluxo on-line após atualizar dependências ou
   publicar uma nova versão.

A comparação de resultados processa arquivos `.xlsx` enviados pelo usuário no
mesmo processo do aplicativo. Use somente exportações confiáveis e configure
limites de upload apropriados para uma instância pública.

## Segredos e variáveis de ambiente

- Copie `.env.example` para `.env`; nunca altere o exemplo com valores reais.
- Armazene somente hashes bcrypt nas variáveis `USER_*`.
- Não registre senhas em texto puro, cookies, exports de sessão ou chaves em
  issues, logs, testes ou commits.
- O `.gitignore` ignora `.env`, mas isso não protege um segredo que já tenha sido
  commitado. Nesse caso, remova-o do histórico quando necessário e troque a
  credencial.
- O carregamento atual usa o `.env` local com sobrescrita habilitada. Se o
  deploy injeta variáveis pelo ambiente, não mantenha um `.env` conflitante no
  diretório da aplicação.

Um hash pode ser gerado sem colocar a senha no comando ou no histórico do
shell:

```bash
python -c "import bcrypt,getpass; print(bcrypt.hashpw(getpass.getpass('Senha: ').encode(), bcrypt.gensalt()).decode())"
```

## Dados e serviços externos

O modo on-line faz requisições de leitura à API pública do Siconfi. O projeto
não inclui token para essa API. Os demonstrativos baixados, resultados e bytes
de exportação podem permanecer temporariamente na memória e no cache do
processo Streamlit.

O modo histórico usa arquivos versionados no repositório e verifica seus hashes
antes de exibi-los. Isso detecta alteração dos recortes, mas não certifica a
correção da fonte original. Consulte [`data/README.md`](data/README.md).

## Dependências

`requirements.txt` fixa somente as dependências diretas. Antes de um deploy,
revise também as dependências transitivas e as vulnerabilidades conhecidas do
ambiente resolvido. O projeto ainda não possui uma política automatizada de
atualização ou varredura de dependências.
