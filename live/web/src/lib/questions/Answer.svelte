<!-- Picks the right way to answer for each of the sixteen question types. -->
<script lang="ts">
	import type { Answer, PublicQuestion, Reveal } from '$lib/types';
	import BlankAnswer from './BlankAnswer.svelte';
	import BlocksAnswer from './BlocksAnswer.svelte';
	import ClockAnswer from './ClockAnswer.svelte';
	import MissingAnswer from './MissingAnswer.svelte';
	import MoneyAnswer from './MoneyAnswer.svelte';
	import PuzzleAnswer from './PuzzleAnswer.svelte';
	import Choices from './Choices.svelte';
	import CountAnswer from './CountAnswer.svelte';
	import SortAnswer from './SortAnswer.svelte';
	import SpellAnswer from './SpellAnswer.svelte';
	import MatchAnswer from './MatchAnswer.svelte';
	import NumberAnswer from './NumberAnswer.svelte';
	import OrderAnswer from './OrderAnswer.svelte';
	import TrueFalse from './TrueFalse.svelte';
	import TypeAnswer from './TypeAnswer.svelte';

	let {
		question,
		disabled = false,
		mine = undefined,
		reveal = null,
		stats = null,
		allRight = false,
		onanswer
	}: {
		question: PublicQuestion;
		disabled?: boolean;
		mine?: Answer;
		reveal?: Reveal | null;
		stats?: Record<string, number> | null;
		allRight?: boolean;
		onanswer?: (answer: Answer) => void;
	} = $props();
</script>

{#key question.id}
	{#if question.type === 'single' || question.type === 'multiple'}
		<Choices choices={question.choices ?? []} multiple={question.type === 'multiple'} pick={question.pick} {disabled} {mine} {reveal} {stats} {onanswer} />
	{:else if question.type === 'truefalse'}
		<TrueFalse {disabled} {mine} {reveal} {stats} {onanswer} />
	{:else if question.type === 'text'}
		<TypeAnswer maxLength={question.maxLength} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'number'}
		<NumberAnswer unit={question.unit} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'order'}
		<OrderAnswer items={question.items ?? []} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'match'}
		<MatchAnswer left={question.left ?? []} right={question.right ?? []} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'blank'}
		<BlankAnswer parts={(question.parts ?? []) as (string | { blank: number })[]} blanks={question.blanks ?? 1} bank={question.bank} {disabled} {mine} {reveal} {allRight} {onanswer} />
	{:else if question.type === 'count'}
		<CountAnswer sticker={question.sticker ?? 'epal'} place={question.place ?? 'bakul'} supply={question.supply ?? 10} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'spell'}
		<SpellAnswer tiles={question.tiles ?? []} length={question.length ?? 0} sticker={question.sticker} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'sort'}
		<SortAnswer groups={question.groups ?? []} items={question.items ?? []} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'missing'}
		<MissingAnswer parts={(question.parts ?? []) as ({ ch: string } | { blank: number })[]} tiles={question.tiles ?? []} blanks={question.blanks ?? 1} sticker={question.sticker} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'puzzle'}
		<PuzzleAnswer pieces={question.pieces ?? []} grid={question.grid ?? 2} sticker={question.sticker} image={question.image} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'blocks'}
		<BlocksAnswer places={question.places ?? ['puluh', 'sa']} {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'clock'}
		<ClockAnswer {disabled} {mine} {reveal} {onanswer} />
	{:else if question.type === 'money'}
		<MoneyAnswer amount={question.amount ?? 0} money={question.money ?? [5, 10, 20, 50]} sticker={question.sticker} {disabled} {mine} {reveal} {onanswer} />
	{/if}
{/key}
