<!-- Picks the right way to answer for each of the eight question types. -->
<script lang="ts">
	import type { Answer, PublicQuestion, Reveal } from '$lib/types';
	import BlankAnswer from './BlankAnswer.svelte';
	import Choices from './Choices.svelte';
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
		<BlankAnswer parts={question.parts ?? []} blanks={question.blanks ?? 1} bank={question.bank} {disabled} {mine} {reveal} {allRight} {onanswer} />
	{/if}
{/key}
