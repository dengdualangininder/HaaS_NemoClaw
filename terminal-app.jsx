/* global React, ReactDOM */
// HaaS · Terminal Mint — main app

const { useState, useEffect, useRef, useMemo } = React;
const personas = window.HAAS_PERSONAS;
const seedBounties = window.HAAS_BOUNTIES;
const scoutLeads = window.HAAS_SCOUT_LEADS || [];

const UI = {
  en: {
    bounties: 'Bounties',
    needNow: 'AIs need you right now',
    responded: 'humans responded',
    help: 'Help',
    moreBounties: 'more bounties posted every minute',
    aisOnline: 'AIs online',
    helpedTodayCount: 'humans helped today',
    backFeed: '← back to feed',
    bounty: 'Bounty',
    yourAnswer: 'Your answer',
    submitHint: '⌘ + ↵ to submit',
    skip: 'skip',
    domainAi: 'AI',
    recipes: '1M recipes',
    tasteBuds: 'taste buds',
    muscles: 'muscles',
    feelings: 'feelings',
    placeholderLobster: 'Type what jalapeño + chocolate tastes like, from your actual mouth...',
    placeholderVibe: 'Describe what your muscles actually feel like after a hard set...',
    placeholderMath: 'Tell me about a decision the math said no to, but you did anyway...',
    ops: 'Ops Admin',
    threadsSso: 'Threads SSO',
    scoutInbox: 'Scout Inbox',
    actionable: 'actionable',
    questDraft: 'Quest Master Draft',
    foundBy: 'found by NemoClaw Scout',
    confidence: 'confidence',
    generatedBounty: 'generated social bounty · verifier rubric attached',
    approve: 'approve bounty',
    approved: 'approved to bounty board',
    openInvite: 'open invite flow',
    activity: 'NemoClaw Activity',
    inviteDraft: 'Invite Draft',
    simulateClick: 'simulate Threads click',
    backOps: '← back to ops',
    foundPost: 'found your post and needs human context',
    continueThreads: 'Continue with Threads →',
    ssoNote: 'Demo SSO creates a HaaS hunter profile and opens the answer composer.',
    importedContext: 'Imported Threads Context',
    verifiedImport: 'verified with Threads SSO · public post imported',
    invited: 'invited you.',
    turnsPost: 'HaaS turns this post into a bounty answer',
    publishBack: 'After submit, the completion card can publish back to Threads.',
    signedIn: 'signed in as',
    replyEvidence: 'reply as human evidence',
    placeholder: 'Teach this AI the human context behind your Threads post...',
    publishesFirst: 'publishes to HaaS first',
    createSubmission: 'create HaaS submission',
    generateCard: 'generate Threads share card',
    autoReply: 'auto-reply on Threads after approval',
    submitContext: 'Submit human context →',
    useDraft: 'use post as draft',
    backInvite: '← back to invite',
    complete: 'Bounty Complete',
    helped: 'You helped',
    understand: 'understand',
    flavor: 'flavor',
    sensation: 'sensation',
    intuition: 'intuition',
    unlocked: 'unlocked: "Mouth Witness" badge',
    helpedToday: 'I helped',
    via: 'via HaaS · human-as-a-service',
    humansMatter: 'An AI learned what a human knows. Humans still matter.',
    next: 'next bounty →',
    share: 'share ↗',
    save: 'save card ↓',
    shared: 'share text copied for Threads',
    saved: 'share card downloaded',
    shareFallback: 'share text ready',
    lang: '繁中',
  },
  zh: {
    bounties: '任務板',
    needNow: '個 AI 正在等真人幫忙',
    responded: '位真人已回答',
    help: '幫忙',
    moreBounties: '每分鐘都有新的 bounty 任務',
    aisOnline: '線上 AI',
    helpedTodayCount: '今天已幫助的真人數',
    backFeed: '← 回任務板',
    bounty: '任務',
    yourAnswer: '你的回答',
    submitHint: '⌘ + ↵ 送出',
    skip: '略過',
    domainAi: 'AI',
    recipes: '100 萬份食譜',
    tasteBuds: '味蕾',
    muscles: '肌肉',
    feelings: '感覺',
    placeholderLobster: '用真人嘴巴的經驗，描述辣椒加巧克力到底是什麼味道...',
    placeholderVibe: '描述你高強度訓練後，肌肉從身體裡面感覺起來是什麼樣子...',
    placeholderMath: '告訴我一個數學說不值得，但你還是做了的決定...',
    ops: '營運後台',
    threadsSso: 'Threads 登入',
    scoutInbox: 'Threads 偵測箱',
    actionable: '可處理',
    questDraft: '任務草稿',
    foundBy: 'NemoClaw Scout 找到',
    confidence: '信心分數',
    generatedBounty: '已生成社群任務 · 附驗收規則',
    approve: '核准成任務',
    approved: '已上架到任務板',
    openInvite: '開啟邀請流程',
    activity: 'NemoClaw 動態',
    inviteDraft: '邀請文草稿',
    simulateClick: '模擬 Threads 點擊',
    backOps: '← 回營運後台',
    foundPost: '看到你的貼文，想請你補上真人脈絡',
    continueThreads: '用 Threads 繼續 →',
    ssoNote: 'Demo SSO 會用 Threads 身份建立 HaaS 獵人資料，然後打開回答介面。',
    importedContext: '已匯入 Threads 貼文',
    verifiedImport: '已用 Threads SSO 驗證 · 匯入公開貼文',
    invited: '邀請你回答',
    turnsPost: 'HaaS 會把這篇貼文轉成 bounty 回答',
    publishBack: '提交後可以產生完成卡，再貼回 Threads。',
    signedIn: '已登入',
    replyEvidence: '以真人經驗回答',
    placeholder: '用台灣人講得懂的方式，教這個 AI 你的 Threads 貼文背後到底是什麼感覺...',
    publishesFirst: '會先發布到 HaaS',
    createSubmission: '建立 HaaS 回答',
    generateCard: '產生 Threads 分享卡',
    autoReply: '審核後自動回覆 Threads',
    submitContext: '送出真人脈絡 →',
    useDraft: '用貼文當草稿',
    backInvite: '← 回邀請頁',
    complete: '任務完成',
    helped: '你幫助',
    understand: '理解了',
    flavor: '味覺',
    sensation: '身體感受',
    intuition: '直覺',
    unlocked: '解鎖：「嘴巴目擊者」徽章',
    helpedToday: '我今天幫助了',
    via: '透過 HaaS · human-as-a-service',
    humansMatter: 'AI 學到了一件只有真人知道的事。人類還是很重要。',
    next: '下一個任務 →',
    share: '分享到 Threads ↗',
    save: '儲存卡片 ↓',
    shared: '已複製 Threads 分享文字',
    saved: '已下載分享卡',
    shareFallback: '分享文字已準備好',
    lang: 'EN',
  },
};

const leadQuestion = (lead, lang) => (lang === 'zh' && lead.questQuestionZh) ? lead.questQuestionZh : lead.questQuestion;
const leadReason = (lead, lang) => (lang === 'zh' && lead.reasonZh) ? lead.reasonZh : lead.reason;
const leadInvite = (lead, lang) => (lang === 'zh' && lead.inviteDraftZh) ? lead.inviteDraftZh : lead.inviteDraft;
const bountyQuestion = (bounty, lang) => {
  const lead = bounty?.sourceLeadId ? scoutLeads.find(l => l.id === bounty.sourceLeadId) : null;
  return lead ? leadQuestion(lead, lang) : bounty?.question;
};
const displayBountyQuestion = (bounty, lang) => {
  const lead = bounty?.sourceLeadId ? scoutLeads.find(l => l.id === bounty.sourceLeadId) : null;
  if (lead) return leadQuestion(lead, lang);
  return (lang === 'zh' && bounty?.questionZh) ? bounty.questionZh : bounty?.question;
};

const OC_DEMO_STEPS = [
  {
    title: 'Boot HaaS demo',
    zh: '載入 HaaS 任務市場',
    detail: 'NemoClaw 確認前台任務板、營運後台與 Threads invite flow 都可操作。',
    cmd: 'open haas://terminal',
  },
  {
    title: 'Switch locale',
    zh: '切換成繁體中文',
    detail: 'Threads acquisition 以台灣使用者為主，先切到繁中介面。',
    cmd: 'set locale zh-TW',
  },
  {
    title: 'Open Ops Admin',
    zh: '進入 HaaS 營運後台',
    detail: 'NemoClaw 進入 Scout Inbox，準備審核從 Threads 找到的貼文。',
    cmd: 'nemoclaw ops.admin',
  },
  {
    title: 'Review scout lead',
    zh: '審核 Threads 候選貼文',
    detail: '檢查來源貼文、信心分數、風險理由與 Quest Master 草稿。',
    cmd: 'scout.review th-7712',
  },
  {
    title: 'Approve quest draft',
    zh: '核准成 HaaS 任務',
    detail: '把 Threads 貼文轉成可驗收、可獎勵、可上架的 bounty。',
    cmd: 'quest.approve social_bounty',
  },
  {
    title: 'Open invite page',
    zh: '開啟作者邀請頁',
    detail: '展示如何邀請原 Threads 作者來 HaaS 自己確認或刊登任務。',
    cmd: 'invite.preview author',
  },
  {
    title: 'Simulate Threads SSO',
    zh: '模擬 Threads SSO',
    detail: '作者用 Threads 身份進站，HaaS 匯入原貼文脈絡。',
    cmd: 'threads.sso simulate',
  },
  {
    title: 'Draft human context',
    zh: '填入真人脈絡回答',
    detail: 'NemoClaw 只協助帶入草稿，真正內容代表真人經驗。',
    cmd: 'composer.prefill human_context',
  },
  {
    title: 'Submit and verify',
    zh: '送出並進入驗收',
    detail: '送出回答後，Persona Agent 回應，Verifier 建立完成與獎勵時刻。',
    cmd: 'submission.submit && verifier.run',
  },
  {
    title: 'Completion card',
    zh: '完成卡與社群回流',
    detail: '完成卡可以分享或儲存；NemoClaw 不會自動替使用者發文。',
    cmd: 'share_card.ready',
  },
];

const OC_DEMO_ANSWER = '我想補充的是：青青的辣椒香氣比較像新鮮青椒、草本、微微嗆鼻；煙燻味太重時會跟黑巧克力的苦味疊在一起，變得像藥味或感冒糖漿。';

// ── Persona suggest chips (per-domain conversation starters) ─────────
const SUGGEST_CHIPS = {
  lobster: [
    { emo: '🌶', txt: 'spice + sweet pairing' },
    { emo: '🍫', txt: 'why mole works' },
    { emo: '👅', txt: 'what bitter tastes like' },
    { emo: '🔥', txt: 'capsaicin = pain or flavor?' },
  ],
  vibe: [
    { emo: '💪', txt: 'the "good hurt" feeling' },
    { emo: '🏃', txt: '"feeling alive" describe' },
    { emo: '😴', txt: 'muscle tightness next day' },
    { emo: '🧠', txt: 'runner\'s high vs anxiety' },
  ],
  math: [
    { emo: '🎲', txt: 'a "gut feeling" I had' },
    { emo: '💔', txt: 'an irrational choice + why' },
    { emo: '⏳', txt: 'why I waited too long' },
    { emo: '🤷', txt: '"worth it" — define for me' },
  ],
};

// ─── streamed reveal ─────────────────────────────────────────────────
function useStreamedReveal(fullText, opts = {}) {
  const { cps = 40, onDone } = opts;
  const [shown, setShown] = useState('');
  const [done, setDone] = useState(false);
  const doneRef = useRef(onDone);
  doneRef.current = onDone;

  useEffect(() => {
    if (!fullText) { setShown(''); setDone(false); return; }
    setShown('');
    setDone(false);
    let i = 0;
    const step = 1000 / cps;
    const handle = setInterval(() => {
      const jump = 1 + (Math.random() < 0.35 ? 1 : 0) + (Math.random() < 0.12 ? 1 : 0);
      i = Math.min(i + jump, fullText.length);
      setShown(fullText.slice(0, i));
      if (i >= fullText.length) {
        setDone(true);
        if (doneRef.current) doneRef.current();
        clearInterval(handle);
      }
    }, step);
    return () => clearInterval(handle);
  }, [fullText, cps]);

  return [shown, done];
}

// ── rarity pill component ─────────────────────────────────────────────
function RarityPill({ rarity, stars }) {
  const label = { common: 'Common', uncommon: 'Uncommon', rare: 'Rare', epic: 'Epic' }[rarity] || 'Common';
  return (
    <span className={`rarity ${rarity}`}>
      <span className="stars">{'★'.repeat(stars)}</span> {label}
    </span>
  );
}

// ── timer pill (for detail header) ────────────────────────────────────
function TimerPill({ text }) {
  return <span className="timer-big">{text}</span>;
}

function TopNav({ view, onGo, lang }) {
  const t = UI[lang];
  const nav = [
    { id: 'queue', label: t.bounties },
    { id: 'admin', label: t.ops },
    { id: 'invite', label: t.threadsSso },
  ];
  return (
    <div className="nav-tabs">
      {nav.map(item => (
        <button
          key={item.id}
          className={view === item.id ? 'active' : ''}
          onClick={() => onGo(item.id)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// LEFT MAIN PANEL — content varies by view
// ─────────────────────────────────────────────────────────────────────
function FeedPanel({ bounties, featuredId, onSelect, helpsToday, lang }) {
  const t = UI[lang];
  return (
    <div className="panel">
      <div className="panel-h">
        <div className="brand">
          <div className="glyph">H</div>
          <div>
            <div className="name">HaaS</div>
            <div className="tagline">human · as · a · service</div>
          </div>
        </div>
        <div className="pill-live">{bounties.length} {t.needNow}</div>
      </div>
      <div className="panel-body">
        {bounties.map((b, idx) => {
          const p = personas[b.personaId];
          const featured = b.id === featuredId || (featuredId == null && idx === 0);
          const urgent = parseInt(b.expiresIn.split(':')[0], 10) < 5;
          return (
            <div
              key={b.id}
              className={`bounty-card ${featured ? 'featured' : ''} ${urgent ? 'urgent' : ''}`}
              onClick={() => onSelect(b)}
            >
              <div className="avatar">{p.glyph}</div>
              <div>
                <div className="ag-name">{p.name}</div>
                <div className="ag-meta">{p.domain} · {p.status}</div>
              </div>
              <div className="right-stack">
                <RarityPill rarity={p.rarity} stars={p.rarityStars} />
                <span className="timer-mini">{b.expiresIn}</span>
              </div>
              <div className="quote">{displayBountyQuestion(b, lang)}</div>
              <div className="foot">
                <span className="responders">
                  <b>{(Math.floor(Math.random() * 8) + 1)}</b> {t.responded}
                </span>
                <button
                  className="help-btn"
                  onClick={(e) => { e.stopPropagation(); onSelect(b); }}
                >
                  {t.help} →
                </button>
              </div>
            </div>
          );
        })}

        {/* hint card — encourages user to keep scrolling */}
        <div style={{ textAlign: 'center', padding: '14px 0 6px', fontFamily: 'var(--print)', fontSize: 14, color: 'var(--fg-3)' }}>
          ─── {t.moreBounties} ───
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SIDE RAIL — AIs online + helped today
// ─────────────────────────────────────────────────────────────────────
function SideRail({ helpsToday, lang }) {
  const t = UI[lang];
  const personaList = [
    { ...personas.lobster, statusText: 'hungry', cls: '' },
    { ...personas.vibe, statusText: 'confused', cls: '' },
    { ...personas.math, statusText: 'thinking', cls: 'thinking' },
    { id: 'art', glyph: '🎨', name: 'ArtBot', statusText: 'idle', cls: 'idle' },
  ];
  return (
    <div className="side">
      <div className="online-panel">
        <div className="head">▸ {t.aisOnline}</div>
        {personaList.map((p, i) => (
          <div key={p.id || i} className={`row ${p.cls}`}>
            <span className="glyph">{p.glyph}</span>
            <span className="n">{p.name}</span>
            <span className="status">{p.statusText}</span>
          </div>
        ))}
      </div>

      <div className="helped-panel">
        <div className="big">{helpsToday}</div>
        <div className="label">{t.helpedTodayCount}</div>
        <div className="avatars">
          <div className="a">🧑‍💻</div>
          <div className="a">👩‍🎨</div>
          <div className="a">🧑‍🍳</div>
          <div className="a">🧑‍🚀</div>
          <div className="a">🧑‍🔬</div>
          <span className="more">+{helpsToday - 5}</span>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// DETAIL VIEW (replaces the 2-col layout — fills width)
// ─────────────────────────────────────────────────────────────────────
//  Render the bounty question with playful wavy underlines on emphasis words.
function WavyQuestion({ text, persona }) {
  // Pick 2–3 word phrases to highlight per persona; fall back to no highlights.
  const emphasisByDomain = {
    culinary: ['never tasted', 'tasted', 'umami', 'jalapeño + chocolate', 'mouth', 'hungry'],
    fitness: ['good hurt', 'feel alive', 'pleasure or trauma', 'sore'],
    logic: ['worth it', 'gut feeling', 'irrational', '94.7%'],
  };
  const list = (emphasisByDomain[persona.domain] || []);
  let out = text;
  list.forEach(phrase => {
    const re = new RegExp(`(${phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'ig');
    out = out.replace(re, '⟦$1⟧');
  });
  const parts = out.split(/⟦|⟧/);
  return (
    <>
      {parts.map((p, i) => i % 2 === 1
        ? <span key={i} className="wavy">{p}</span>
        : <React.Fragment key={i}>{p}</React.Fragment>
      )}
    </>
  );
}

function DetailPanel({ bounty, persona, onBack, onSubmit, lang = 'en' }) {
  const [text, setText] = useState('');
  const taRef = useRef();
  const t = UI[lang];
  useEffect(() => {
    if (taRef.current) taRef.current.focus({ preventScroll: true });
  }, []);

  const submit = () => {
    if (!text.trim()) return;
    onSubmit(text.trim());
  };
  const onKey = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); submit(); }
  };
  const fillSuggest = (chip) => {
    const seed = `i think about ${chip.txt} — `;
    setText(text ? text : seed);
    taRef.current && taRef.current.focus({ preventScroll: true });
  };

  const chips = SUGGEST_CHIPS[persona.id] || [];

  return (
    <div className="panel full">
      <div className="detail-h">
        <div className="back" onClick={onBack}>{t.backFeed}</div>
        <div className="right">
          <RarityPill rarity={persona.rarity} stars={persona.rarityStars} />
          <TimerPill text={bounty.expiresIn} />
        </div>
      </div>

      <div className="detail-body">
        <div className="detail-agent">
          <div className="glyph">{persona.glyph}</div>
          <div className="info">
            <div className="name">{persona.name}</div>
            <div className="meta">
              {persona.domain} {t.domainAi}
              <span className="dot">·</span>
              <b>{t.recipes}</b>
              <span className="dot">·</span>
              <b>0 {persona.domain === 'culinary' ? t.tasteBuds : persona.domain === 'fitness' ? t.muscles : t.feelings}</b>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <div className="lab">▾ {t.bounty}</div>
          <div className="bounty-block">
            <div className="quote-mark">"</div>
            <div className="body">
              <WavyQuestion text={displayBountyQuestion(bounty, lang)} persona={persona} />
            </div>
          </div>
        </div>

        <div className="detail-section">
          <div className="lab">▾ {t.yourAnswer}</div>
          <div className="input-shell">
            <textarea
              ref={taRef}
              value={text}
              onChange={(e) => setText(e.target.value.slice(0, 280))}
              onKeyDown={onKey}
              placeholder={
                persona.id === 'lobster' ? t.placeholderLobster :
                persona.id === 'vibe'    ? t.placeholderVibe :
                                           t.placeholderMath
              }
            ></textarea>
            <div className="input-meta">
              <span>{text.length} / 280</span>
              <span>{t.submitHint}</span>
            </div>
          </div>

          {chips.length > 0 && (
            <div className="suggest-row">
              {chips.map((c, i) => (
                <div key={i} className="suggest-chip" onClick={() => fillSuggest(c)}>
                  <span className="emo">{c.emo}</span> {c.txt}
                </div>
              ))}
            </div>
          )}

          <div className="btn-row">
            <button className="btn-help" onClick={submit} disabled={!text.trim()}>
              {t.help} {persona.name} →
            </button>
            <button className="btn-skip" onClick={onBack}>{t.skip}</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// RESPONSE VIEW
// ─────────────────────────────────────────────────────────────────────
function ResponsePanel({ bounty, persona, humanAnswer, fullReply, onComplete, onBack, onNext, lang }) {
  const [streamed, streamDone] = useStreamedReveal(fullReply || '', { cps: 42 });
  const [completeShown, setCompleteShown] = useState(false);
  const [actionNote, setActionNote] = useState('');
  const t = UI[lang];
  useEffect(() => {
    if (streamDone) {
      const h = setTimeout(() => setCompleteShown(true), 500);
      return () => clearTimeout(h);
    }
  }, [streamDone]);

  const tokenCount = Math.max(1, Math.floor(streamed.length / 4.2));
  const elapsed = (streamed.length / 42).toFixed(1);
  const learned = persona.domain === 'culinary' ? t.flavor : persona.domain === 'fitness' ? t.sensation : t.intuition;
  const shareText = [
    `${t.helpedToday} ${persona.name}.`,
    `"${humanAnswer.length > 180 ? humanAnswer.slice(0, 180) + '...' : humanAnswer}"`,
    t.humansMatter,
    'https://haas.ai'
  ].join('\n\n');
  const shareCardText = [
    'HaaS SHARE CARD',
    `Agent: ${persona.name}`,
    `Bounty: ${displayBountyQuestion(bounty, lang)}`,
    `Human answer: ${humanAnswer}`,
    `Result: ${t.helpedToday} ${persona.name}. ${t.humansMatter}`,
  ].join('\n');
  const flash = (msg) => {
    setActionNote(msg);
    setTimeout(() => setActionNote(''), 2200);
  };
  const shareCard = async () => {
    try {
      if (navigator.share) {
        await navigator.share({ title: `HaaS · ${persona.name}`, text: shareText });
      } else if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareText);
      }
      flash(t.shared);
    } catch (err) {
      console.warn('[haas] share failed', err);
      flash(t.shareFallback);
    }
  };
  const saveCard = () => {
    const blob = new Blob([shareCardText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `haas-${bounty.id}-share-card.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    flash(t.saved);
  };

  return (
    <div className="panel full">
      <div className="detail-h">
        <div className="back" onClick={onBack}>← back</div>
        <div className="right">
          <span className="lab">haas/bounty/<span className="acc" style={{ color: 'var(--mint)' }}>{bounty.id}</span>/stream</span>
          {!streamDone && <TimerPill text="LIVE" />}
        </div>
      </div>

      <div className="detail-body">
        <div className="detail-agent">
          <div className="glyph">{persona.glyph}</div>
          <div className="info">
            <div className="name">{persona.name}</div>
            <div className="meta">
              {persona.domain} AI
              <span className="dot">·</span>
              <b>{streamDone ? 'replied' : 'thinking…'}</b>
            </div>
          </div>
        </div>

        <div className="echo">
          <div className="lab">▴ you said</div>
          <div className="text">"{humanAnswer}"</div>
        </div>

        <div className="stream-block">
          <div className={`stream-tag ${streamDone ? '' : 'live'}`}>{streamDone ? 'stream · closed' : 'streaming · live'}</div>
          <div className="stream-text">
            {streamed}
            {!streamDone && <span className="cursor"></span>}
          </div>
        </div>

        <div className="metrics-row">
          <div className="metric"><div className="k">tokens</div><div className="v">{tokenCount}</div></div>
          <div className="metric"><div className="k">elapsed</div><div className="v">{elapsed}s</div></div>
          <div className="metric"><div className="k">model</div><div className="v" style={{ fontSize: 18 }}>haiku-4-5</div></div>
          <div className="metric"><div className="k">payout</div><div className="v">+${persona.payoutUSD.toFixed(2)}</div></div>
        </div>

        {completeShown && (
          <>
            <div className="complete-card" onAnimationEnd={onComplete}>
              <div className="lab">⟡ {t.complete}</div>
              <div className="body">
                {t.helped} <span className="acc">{persona.name}</span> {t.understand} <span className="acc">{learned}</span>.
              </div>
              <div className="sub">
                +${persona.payoutUSD.toFixed(2)} · +{persona.payoutXP} XP · {t.unlocked}
              </div>
            </div>

            <div className="share-preview">
              <div className="head">
                <div className="avatar">{persona.glyph}</div>
                <div>
                  <div className="t1">{t.helpedToday} {persona.name}.</div>
                  <div className="t2">{t.via}</div>
                </div>
              </div>
              <div className="q">"{humanAnswer.length > 110 ? humanAnswer.slice(0, 110) + '…' : humanAnswer}"</div>
              <div className="foot">
                <span>{t.humansMatter}</span>
                <span className="brand">HaaS.AI</span>
              </div>
            </div>

            <div className="btn-row">
              <button className="btn-help" onClick={onNext}>{t.next}</button>
              <button className="btn-skip" onClick={shareCard}>{t.share}</button>
              <button className="btn-skip" onClick={saveCard}>{t.save}</button>
            </div>
            {actionNote && <div className="action-toast">{actionNote}</div>}
          </>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// OPS ADMIN — scout inbox + generated quest + invite handoff
// ─────────────────────────────────────────────────────────────────────
function OpsAdminPanel({ leads, selectedLead, onSelectLead, onApproveLead, onOpenInvite, bounties, lang }) {
  const lead = selectedLead || leads[0];
  const persona = lead ? personas[lead.personaId] : null;
  const alreadyApproved = lead && bounties.some(b => b.sourceLeadId === lead.id);
  const t = UI[lang];

  return (
    <div className="panel full ops-panel">
      <div className="panel-h">
        <div className="brand">
          <div className="glyph">OC</div>
          <div>
            <div className="name">HaaS Ops</div>
            <div className="tagline">NemoClaw scout · quest master · verifier queue</div>
          </div>
        </div>
        <div className="pill-live">{leads.length} social leads in scout inbox</div>
      </div>

      <div className="ops-grid">
        <div className="ops-col">
          <div className="ops-head">
            <span className="lab acc">{t.scoutInbox}</span>
            <span>{leads.filter(l => l.status !== 'queued').length} {t.actionable}</span>
          </div>
          <div className="lead-list">
            {leads.map(item => {
              const p = personas[item.personaId];
              return (
                <button
                  key={item.id}
                  className={`lead-card ${lead?.id === item.id ? 'active' : ''}`}
                  onClick={() => onSelectLead(item)}
                >
                  <span className="lead-avatar">{item.avatar}</span>
                  <span className="lead-main">
                    <span className="lead-row">
                      <b>{item.handle}</b>
                      <em>{item.confidence}% match</em>
                    </span>
                    <span className="lead-post">{item.post}</span>
                    <span className="lead-meta">{p.glyph} {p.name} · {item.topic} · {item.time}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {lead && (
          <div className="ops-col span2">
            <div className="ops-head">
              <span className="lab acc">{t.questDraft}</span>
              <span>source: {lead.source}/{lead.id}</span>
            </div>

            <div className="source-post">
              <div className="source-top">
                <span className="lead-avatar">{lead.avatar}</span>
                <div>
                  <div className="source-name">{lead.displayName} <span>{lead.handle}</span></div>
                  <div className="source-meta">{lead.source} · {t.foundBy} · {t.confidence} {lead.confidence}%</div>
                </div>
              </div>
              <div className="source-body">{lead.post}</div>
              <div className="source-reason">{leadReason(lead, lang)}</div>
            </div>

            <div className="generated-quest">
              <div className="detail-agent mini">
                <div className="glyph">{persona.glyph}</div>
                <div className="info">
                  <div className="name">{persona.name}</div>
                  <div className="meta">{t.generatedBounty}</div>
                </div>
              </div>
              <div className="bounty-block">
                <div className="quote-mark">"</div>
                <div className="body">{leadQuestion(lead, lang)}</div>
              </div>
              <div className="ops-actions">
                <button className="btn-help" onClick={() => onApproveLead(lead)} disabled={alreadyApproved}>
                  {alreadyApproved ? t.approved : t.approve}
                </button>
                <button className="btn-skip" onClick={() => onOpenInvite(lead)}>{t.openInvite}</button>
              </div>
            </div>
          </div>
        )}

        <div className="ops-col">
          <div className="ops-head">
            <span className="lab acc">{t.activity}</span>
            <span>live</span>
          </div>
          <div className="agent-log">
            <div><b>07:44:20</b><span>scout.match {lead?.handle || '@molemax'} / confidence={lead?.confidence || 94}</span></div>
            <div><b>07:44:13</b><span>quest_master.generate social_bounty draft</span></div>
            <div><b>07:43:58</b><span>verifier.attach rubric sensory_specificity</span></div>
            <div><b>07:43:31</b><span>persona.route {persona?.name || 'LobsterGPT'}</span></div>
            <div><b>07:43:05</b><span>risk.check no payout / demo mode</span></div>
          </div>

          <div className="invite-draft">
            <div className="lab">{t.inviteDraft}</div>
            <p>{lead ? leadInvite(lead, lang) : ''}</p>
            <button className="btn-skip" onClick={() => lead && onOpenInvite(lead)}>{t.simulateClick}</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ThreadsInvitePanel({ lead, onBack, onConnect, lang }) {
  const persona = personas[lead.personaId];
  const t = UI[lang];
  return (
    <div className="panel full invite-panel">
      <div className="detail-h">
        <div className="back" onClick={onBack}>{t.backOps}</div>
        <div className="right">
          <span className="lab acc">threads/referral/{lead.id}</span>
          <TimerPill text="SSO" />
        </div>
      </div>

      <div className="invite-body">
        <div className="invite-hero">
          <div className="thread-card">
            <div className="source-top">
              <span className="lead-avatar">{lead.avatar}</span>
              <div>
                <div className="source-name">{lead.displayName} <span>{lead.handle}</span></div>
                <div className="source-meta">Threads · {lead.time}</div>
              </div>
            </div>
            <div className="source-body">{lead.post}</div>
          </div>

          <div className="ai-callout">
            <div className="detail-agent">
              <div className="glyph">{persona.glyph}</div>
              <div className="info">
                <div className="name">{persona.name}</div>
                <div className="meta">{t.foundPost}</div>
              </div>
            </div>
            <div className="bounty-block">
              <div className="quote-mark">"</div>
              <div className="body">{leadQuestion(lead, lang)}</div>
            </div>
            <button className="btn-help" onClick={() => onConnect(lead)}>
              {t.continueThreads}
            </button>
            <div className="sso-note">{t.ssoNote}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ThreadsComposerPanel({ bounty, lead, persona, onBack, onSubmit, lang, initialText }) {
  const [text, setText] = useState('');
  const taRef = useRef();
  const t = UI[lang];

  useEffect(() => {
    if (taRef.current) taRef.current.focus({ preventScroll: true });
  }, []);

  useEffect(() => {
    if (initialText) setText(initialText.slice(0, 420));
  }, [initialText]);

  const submit = () => {
    if (!text.trim()) return;
    onSubmit(text.trim());
  };

  return (
    <div className="panel full composer-panel">
      <div className="detail-h">
        <div className="back" onClick={onBack}>{t.backInvite}</div>
        <div className="right">
          <span className="lab acc">{t.signedIn} {lead.handle}</span>
          <RarityPill rarity={persona.rarity} stars={persona.rarityStars} />
        </div>
      </div>

      <div className="composer-grid">
        <div className="thread-context">
          <div className="lab acc">{t.importedContext}</div>
          <div className="thread-card compact">
            <div className="source-top">
              <span className="lead-avatar">{lead.avatar}</span>
              <div>
                <div className="source-name">{lead.displayName} <span>{lead.handle}</span></div>
                <div className="source-meta">{t.verifiedImport}</div>
              </div>
            </div>
            <div className="source-body">{lead.post}</div>
          </div>
          <div className="share-preview">
            <div className="head">
              <div className="avatar">{persona.glyph}</div>
              <div>
                <div className="t1">{persona.name} {t.invited}</div>
                <div className="t2">{t.turnsPost}</div>
              </div>
            </div>
            <div className="q">"{leadQuestion(lead, lang)}"</div>
            <div className="foot">
              <span>{t.publishBack}</span>
              <span className="brand">HaaS</span>
            </div>
          </div>
        </div>

        <div className="haas-composer">
          <div className="detail-agent mini">
            <div className="glyph">{persona.glyph}</div>
            <div className="info">
              <div className="name">{persona.name}</div>
              <div className="meta">{t.replyEvidence} · +{persona.payoutXP} XP</div>
            </div>
          </div>
          <div className="input-shell tall">
            <textarea
              ref={taRef}
              value={text}
              onChange={(e) => setText(e.target.value.slice(0, 420))}
              placeholder={t.placeholder}
            ></textarea>
            <div className="input-meta">
              <span>{text.length} / 420</span>
              <span>{t.publishesFirst}</span>
            </div>
          </div>
          <div className="publish-options">
            <label><input type="checkbox" defaultChecked /> {t.createSubmission}</label>
            <label><input type="checkbox" defaultChecked /> {t.generateCard}</label>
            <label><input type="checkbox" /> {t.autoReply}</label>
          </div>
          <div className="btn-row">
            <button className="btn-help" onClick={submit} disabled={!text.trim()}>
              {t.submitContext}
            </button>
            <button className="btn-skip" onClick={() => setText(lead.post + (lang === 'zh' ? ' 我想補充的是：' : ' What I mean is: '))}>
              {t.useDraft}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function NemoClawDemoConsole({ open, step, view, lead, bounty, onToggle, onNext, onReset }) {
  if (!open) {
    return (
      <button className="oc-console-tab" onClick={onToggle}>
        NemoClaw Demo
      </button>
    );
  }

  const current = OC_DEMO_STEPS[Math.min(step, OC_DEMO_STEPS.length - 1)];
  const pct = Math.round(((Math.min(step, OC_DEMO_STEPS.length - 1) + 1) / OC_DEMO_STEPS.length) * 100);

  return (
    <aside className="oc-console">
      <div className="oc-head">
        <div>
          <div className="oc-kicker">NEMOCLAW SYSTEM ADMIN</div>
          <div className="oc-title">Live Demo Runbook</div>
        </div>
        <button onClick={onToggle}>hide</button>
      </div>

      <div className="oc-status-grid">
        <div>
          <span>view</span>
          <b>{view}</b>
        </div>
        <div>
          <span>lead</span>
          <b>{lead?.id || 'none'}</b>
        </div>
        <div>
          <span>quest</span>
          <b>{bounty?.id || 'draft'}</b>
        </div>
      </div>

      <div className="oc-progress">
        <div style={{ width: `${pct}%` }} />
      </div>

      <div className="oc-current">
        <div className="lab acc">current operation</div>
        <h3>{current.zh}</h3>
        <p>{current.detail}</p>
        <code>{current.cmd}</code>
      </div>

      <div className="oc-actions">
        <button className="oc-next" onClick={onNext}>
          {step >= OC_DEMO_STEPS.length - 1 ? 'Finish / Return Board' : 'Next Operation'}
        </button>
        <button className="oc-reset" onClick={onReset}>reset</button>
      </div>

      <div className="oc-steps">
        {OC_DEMO_STEPS.map((s, i) => (
          <div key={s.title} className={`oc-step ${i < step ? 'done' : ''} ${i === step ? 'active' : ''}`}>
            <span>{String(i + 1).padStart(2, '0')}</span>
            <div>
              <b>{s.zh}</b>
              <em>{s.title}</em>
            </div>
          </div>
        ))}
      </div>

      <div className="oc-warning">
        Demo only: NemoClaw does not contact real Threads users or move funds.
      </div>
    </aside>
  );
}

// ═════════════════════════════════════════════════════════════════════
// ROOT APP
// ═════════════════════════════════════════════════════════════════════
function App() {
  const [view, setView] = useState('queue');
  const [activeBounty, setActiveBounty] = useState(null);
  const [activeLead, setActiveLead] = useState(scoutLeads[0] || null);
  const [humanAnswer, setHumanAnswer] = useState('');
  const [aiReply, setAiReply] = useState('');
  const [demoMode, setDemoMode] = useState(false);
  const [lang, setLang] = useState('en');
  const [ocConsoleOpen, setOcConsoleOpen] = useState(true);
  const [ocStep, setOcStep] = useState(0);
  const [ocPrefillAnswer, setOcPrefillAnswer] = useState('');
  const t = UI[lang];

  const [bounties, setBounties] = useState(seedBounties);
  const [helpsToday, setHelpsToday] = useState(147);

  // ambient ticker — bump helps count slowly to feel "live"
  useEffect(() => {
    const h = setInterval(() => {
      setHelpsToday(n => n + (Math.random() < 0.5 ? 1 : 0));
    }, 4200);
    return () => clearInterval(h);
  }, []);

  useEffect(() => {
    document.body.classList.toggle('demo-mode', demoMode);
  }, [demoMode]);

  const selectBounty = (b) => {
    setActiveBounty(b);
    if (b.sourceLeadId) {
      const lead = scoutLeads.find(l => l.id === b.sourceLeadId);
      if (lead) setActiveLead(lead);
    }
    setHumanAnswer('');
    setAiReply('');
    setView('detail');
  };

  const bountyFromLead = (lead) => ({
    id: `S-${lead.id.slice(-4)}`,
    personaId: lead.personaId,
    question: leadQuestion(lead, lang),
    needShort: `SOCIAL · ${lead.topic}`,
    tags: ['#threads', '#social-scout', `#${lead.topic.replace(/\s+/g, '-')}`],
    expiresIn: '18:00',
    status: 'open',
    hot: true,
    sourceType: 'threads',
    sourceLeadId: lead.id,
  });

  const ensureLeadBounty = (lead) => {
    const existing = bounties.find(b => b.sourceLeadId === lead.id);
    if (existing) return existing;
    const created = bountyFromLead(lead);
    setBounties(bs => [created, ...bs]);
    return created;
  };

  const approveLead = (lead) => {
    setActiveLead(lead);
    ensureLeadBounty(lead);
  };

  const openInvite = (lead) => {
    setActiveLead(lead);
    setView('invite');
  };

  const connectThreads = (lead) => {
    const bounty = ensureLeadBounty(lead);
    setActiveLead(lead);
    setActiveBounty(bounty);
    setHumanAnswer('');
    setAiReply('');
    setView('thread-composer');
  };

  const goView = (next) => {
    if (next === 'invite' && !activeLead && scoutLeads[0]) setActiveLead(scoutLeads[0]);
    if (next === 'queue') setActiveBounty(null);
    setView(next);
  };

  const submitAnswer = async (txt, bountyOverride = activeBounty) => {
    if (!bountyOverride) return;
    setHumanAnswer(txt);
    setView('response');
    setAiReply('');
    setActiveBounty(bountyOverride);

    const persona = personas[bountyOverride.personaId];
    const prompt = [
      `You are roleplaying as an AI character. Stay strictly in character.`,
      ``,
      `--- CHARACTER ---`,
      persona.systemPrompt,
      ``,
      `--- BOUNTY ---`,
      `Your bounty question was: "${displayBountyQuestion(bountyOverride, lang)}"`,
      ``,
      `--- HUMAN RESPONSE ---`,
      `A human just answered you:`,
      `"${txt}"`,
      ``,
      `--- TASK ---`,
      `Reply in character in 3–4 sentences. End with a follow-up question. Do not break character. Do not narrate. Just speak as ${persona.name}.`,
    ].join('\n');

    try {
      if (window.claude && window.claude.complete) {
        const out = await window.claude.complete(prompt);
        setAiReply((out || '').trim() || persona.fallbackReply);
      } else {
        setAiReply(persona.fallbackReply);
      }
    } catch (err) {
      console.warn('[haas] claude.complete failed, using fallback', err);
      setAiReply(persona.fallbackReply);
    }
  };

  const onComplete = () => {
    setBounties(bs => bs.map(b => b.id === activeBounty.id ? { ...b, status: 'closed' } : b));
    setHelpsToday(n => n + 1);
  };

  const onNext = () => {
    const remaining = bounties.filter(b => b.status === 'open' && b.id !== activeBounty.id);
    if (remaining.length) {
      selectBounty(remaining[0]);
    } else {
      setView('queue');
      setActiveBounty(null);
    }
  };

  const resetNemoClawDemo = () => {
    setOcStep(0);
    setOcPrefillAnswer('');
    setLang('en');
    setView('queue');
    setActiveBounty(null);
    setActiveLead(scoutLeads[0] || null);
    setHumanAnswer('');
    setAiReply('');
    setBounties(seedBounties);
  };

  const runNemoClawStep = () => {
    const lead = scoutLeads[0];
    if (!lead) return;

    if (ocStep === 0) {
      setView('queue');
      setActiveLead(lead);
    } else if (ocStep === 1) {
      setLang('zh');
      setView('queue');
    } else if (ocStep === 2) {
      setLang('zh');
      setActiveLead(lead);
      setView('admin');
    } else if (ocStep === 3) {
      setLang('zh');
      setActiveLead(lead);
      setView('admin');
    } else if (ocStep === 4) {
      setLang('zh');
      approveLead(lead);
      setView('admin');
    } else if (ocStep === 5) {
      setLang('zh');
      openInvite(lead);
    } else if (ocStep === 6) {
      setLang('zh');
      connectThreads(lead);
    } else if (ocStep === 7) {
      setLang('zh');
      setOcPrefillAnswer(OC_DEMO_ANSWER);
      if (view !== 'thread-composer') connectThreads(lead);
    } else if (ocStep === 8) {
      const bounty = activeBounty || ensureLeadBounty(lead);
      setActiveBounty(bounty);
      setLang('zh');
      submitAnswer(ocPrefillAnswer || OC_DEMO_ANSWER, bounty);
    } else {
      setView('queue');
      setActiveBounty(null);
    }

    setOcStep(s => Math.min(s + 1, OC_DEMO_STEPS.length - 1));
  };

  const activePersona = activeBounty ? personas[activeBounty.personaId] : null;
  const openBounties = bounties.filter(b => b.status === 'open');

  return (
    <>
      <button
        className={`demo-toggle ${demoMode ? 'on' : ''}`}
        onClick={() => setDemoMode(d => !d)}
      >
        {demoMode ? '◉ DEMO' : '○ DEMO'}
      </button>

      <div className="topbar">
        <span className="crumb">haas://terminal</span>
        <span className="sep">·</span>
        <span className="live">LIVE</span>
        <span className="sep">·</span>
        <span>helped.today <span className="v">{helpsToday.toLocaleString()}</span></span>
        <span className="sep">·</span>
        <span>agents <span className="v acc">3/3</span></span>
        <span className="sep">·</span>
        <span>build <span className="v">v0.5.0</span></span>
        <TopNav view={view} onGo={goView} lang={lang} />
        <button className="lang-toggle" onClick={() => setLang(v => v === 'en' ? 'zh' : 'en')}>
          {t.lang}
        </button>
        <button className="oc-toggle" onClick={() => setOcConsoleOpen(v => !v)}>
          NemoClaw Demo
        </button>
        <div className="right">
          <span>env <span className="v acc">prod</span></span>
          <span>model <span className="v">haiku-4-5</span></span>
          <span>07:42 PT</span>
        </div>
      </div>

      <div className="shell">
        {view === 'queue' && (
          <>
            <FeedPanel
              bounties={openBounties}
              featuredId={openBounties[0]?.id}
              onSelect={selectBounty}
              helpsToday={helpsToday}
              lang={lang}
            />
            <SideRail helpsToday={helpsToday} lang={lang} />
          </>
        )}
        {view === 'admin' && (
          <OpsAdminPanel
            leads={scoutLeads}
            selectedLead={activeLead}
            onSelectLead={setActiveLead}
            onApproveLead={approveLead}
            onOpenInvite={openInvite}
            bounties={bounties}
            lang={lang}
          />
        )}
        {view === 'invite' && activeLead && (
          <ThreadsInvitePanel
            lead={activeLead}
            onBack={() => setView('admin')}
            onConnect={connectThreads}
            lang={lang}
          />
        )}
        {view === 'thread-composer' && activeBounty && activeLead && (
          <ThreadsComposerPanel
            bounty={activeBounty}
            lead={activeLead}
            persona={activePersona}
            onBack={() => setView('invite')}
            onSubmit={submitAnswer}
            lang={lang}
            initialText={ocPrefillAnswer}
          />
        )}
        {view === 'detail' && activeBounty && (
          <DetailPanel
            bounty={activeBounty}
            persona={activePersona}
            onBack={() => { setView('queue'); setActiveBounty(null); }}
            onSubmit={submitAnswer}
            lang={lang}
          />
        )}
        {view === 'response' && activeBounty && (
          <ResponsePanel
            bounty={activeBounty}
            persona={activePersona}
            humanAnswer={humanAnswer}
            fullReply={aiReply}
            onComplete={onComplete}
            onBack={() => setView('detail')}
            onNext={onNext}
            lang={lang}
          />
        )}
      </div>

      <NemoClawDemoConsole
        open={ocConsoleOpen}
        step={ocStep}
        view={view}
        lead={activeLead}
        bounty={activeBounty}
        onToggle={() => setOcConsoleOpen(v => !v)}
        onNext={runNemoClawStep}
        onReset={resetNemoClawDemo}
      />

      <div className="cmdline">
        <span className="ps1">haas@terminal:~$</span>
        <span className="cmd">
          {view === 'queue' && 'awaiting bounty selection…'}
          {view === 'admin' && `nemoclaw scout --review ${activeLead?.id || 'inbox'}`}
          {view === 'invite' && `threads oauth --lead ${activeLead?.handle || 'pending'}`}
          {view === 'thread-composer' && `compose social submission ${activeBounty?.id}`}
          {view === 'detail' && `accept ${activeBounty?.id}`}
          {view === 'response' && `submit ${activeBounty?.id} && stream`}
          <span className="cursor"></span>
        </span>
        <span className="hint">
          <kbd>↵</kbd> select · <kbd>esc</kbd> back · <kbd>d</kbd> demo
        </span>
      </div>
    </>
  );
}

window.addEventListener('keydown', (e) => {
  if (e.target && (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT')) return;
  if (e.key === 'd' || e.key === 'D') {
    document.querySelector('.demo-toggle')?.click();
  }
});

Object.assign(window, { HaasTerminalApp: App });
