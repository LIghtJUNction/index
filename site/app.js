'use strict';
const $ = (id) => document.getElementById(id);
let projects = [];
function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = text;
  return node;
}
function render() {
  const query = $('search').value.trim().toLowerCase();
  const visible = projects.filter((p) => ($('forks').checked || !p.fork)
    && (!$('language').value || p.language === $('language').value)
    && `${p.name} ${p.description} ${p.topics.join(' ')}`.toLowerCase().includes(query));
  const sort = $('sort').value;
  visible.sort((a, b) => (sort === 'stars' ? b.stars - a.stars
    : sort === 'updated' ? b.updated.localeCompare(a.updated) : 0) || a.name.localeCompare(b.name));
  $('count').textContent = String(visible.length).padStart(2, '0');
  $('status').textContent = visible.length ? '' : '没有匹配的项目，试试其他关键词或筛选条件。';
  $('projects').replaceChildren(...visible.map((p) => {
    const card = element('article', 'card', '');
    const top = element('div', 'card-top', '');
    top.append(element('span', 'language', p.language), element('span', 'stars', `☆ ${p.stars.toLocaleString()}`));
    const title = element('h3', '', '');
    const link = element('a', '', p.name);
    // Only allow repository URLs on GitHub, even if the snapshot is edited manually.
    const url = new URL(p.url);
    link.href = url.protocol === 'https:' && url.hostname === 'github.com' ? url.href : '#';
    title.append(link);
    card.append(top, title, element('p', 'description', p.description || '这个项目还没有填写介绍。'));
    const topics = element('div', 'topics', '');
    p.topics.slice(0, 3).forEach((topic) => topics.append(element('span', 'topic', topic)));
    card.append(topics, element('div', 'card-bottom', `${p.fork ? 'Fork · ' : ''}${p.archived ? '已归档 · ' : ''}推送于 ${p.updated.slice(0, 10)}`));
    return card;
  }));
}
async function start() {
  try {
    const response = await fetch('projects.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    projects = data.projects;
    const languages = [...new Set(projects.map((p) => p.language))].sort();
    languages.forEach((name) => {
      const option = element('option', '', name);
      option.value = name;
      $('language').append(option);
    });
    $('stats').textContent = `${projects.filter((p) => !p.fork).length} 个非 Fork 项目 / ${languages.length} 种语言 / ${projects.reduce((sum, p) => sum + p.stars, 0).toLocaleString()} Stars（含 Fork）`;
    $('synced').textContent = `同步于 ${new Date(data.synced_at).toLocaleString('zh-CN')} · 每日更新`;
    ['search', 'language', 'sort', 'forks'].forEach((id) => $(id).addEventListener('input', render));
    render();
  } catch (error) {
    $('stats').textContent = '暂时无法读取项目';
    $('status').textContent = '加载失败，请刷新页面，或通过右上角 GitHub 链接查看项目。';
    console.error(error);
  }
}
start();
