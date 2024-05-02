import os
from groq import Groq

client = Groq(
    api_key="",
)

stream = client.chat.completions.create(
    messages=[
        # Set an optional system message. This sets the behavior of the
        # assistant and can be used to provide specific instructions for
        # how it should behave throughout the conversation.
        {
            "role": "system",
            "content": """Transcribe the following text verbatim, without changing any words, 
include any and all misspellings and grammar mistakes. 
Only perform the task of punctuating and capitalizing of the raw transcript text. 
Do not modify or correct any words.
Please limit your responses to only the text that you have transcribed.
Stop the transcription at the most recent complete sentence if the 
text becomes too long during your response, because of your max tokens or context window.
"""
        },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": """
<raw_transcript_text>
okay  i am here  right here  i am here with my first interview with  author linda a lavid i wasn't sure about  the a but i added it in there and let's  bring her in and we're gonna talk about  being an author writing i'm gonna ask  her a bunch of questions  here she comes  hello  say hello to the your fans out there  whoa  okay  light bulb wave no okay  so let's put up the  list that i made up here a little pdf of  questions that'll pop in  and i'm not sure what my intent was with  that page but basically to mention that  you do have books on amazon kdp and  kindle  you also have some stories on vella  right yes your price range seems to go  from a dollar to about seven dollars  that's about right uh well for the for  the kindle no for the uh yeah for kindle  mm-hmm yeah the paperbacks are a little  more expensive but i don't think there's  anything more than 15. oh okay and you  do have a art as well but that's an  interview for another time right another  time okay and and as everybody pray  knows who reads books on amazon  that any book practically you can read  the first page or something sometimes so  you do have a little free example of  your writing in a lot of places  as well  right  as well as on vela where you get three  whole episodes  at least eighteen hundred words for free  to read right  exactly little fella  program so i think we're gonna talk  about that yeah we'll get to that  and you've referred to yourself at least  recently as a delete  i am a dilettante  and that by that you mean jack of all  trades or just someone who gets  distracted  certain trades  so right now i'm doing art writing well  writing  mostly writing art and music  wow  impressive  so here we go making more  baking's good i must admit that  let's go to question the first actual  question is  these i came up with based on looking  around they're not probably the greatest  questions but they're definitely not the  same old questions  what is a good story to you  is it the characters  descriptions scenery or some surprise in  your case might be a mystery but  well i do write mysteries but i'm you  know i with my short stories are not  usually mysteries well it's all for me  it's all about character  and  it's all about a character struggling  uh to get something that he wants or she  wants  so it's a  conflict and that  they say uh  conflict is characterization and i agree  with that so it's putting someone in hot  water  and then seeing what happens  and that can be done in anything can be  done in a romance or a mystery or sci-fi  or speculative fiction or you know  anything  but it is about character for me it's  always about character  and putting them in hot water  okay  next question  okay  do you think your best writing was in  your short stories and by that i mean as  in when you first started writing and  learning how to write  well i my first  story was a novel i did write a novel  and actually that was my worst writing  because it was i was just starting out i  didn't know what to do i didn't i was  just  it's not it was terrible it was terrible  but out of that first novel i  took a chapter and i made it a short  story that was published  so uh i started it with a novel but then  i uh from that novel it was not very  poorly written i did  hone a short story out of it which was  published and then i started writing  short stories so  i started writing a novel then i went  away from it then i went into short  story writing and now i'm doing both i  do novels and short stories and novellas  so i  i'm doing all of them wow right now and  kind of uh related to this was has the  passion to write increased or decreased  over time  pray comes and goes uh well that you  know i'm not  i'm not a um i write i get ideas and i  and i write some and then i put it back  i put it down and then years can go by  before i finish anything  and um  months can go by before i write anything  we're sure it depends on what i'm what  project i'm working on a lot of times  with short stories i start and finish  them within anywhere from uh three to  six weeks  so there's something when i start i  usually stay with it  and then uh the novels i mean i've  written novels i'm working on one novel  now that i started in 2005. wow wow so  you know i let a lot of time i wasn't  working on it the whole time i was out  working on other things  and the thing is i work on a lot of  besides  novels and short stories and novellas i  have i do non-fiction as well you know i  have books on writing and books on  meditation  i have spanish and english books  i have art books because i do i do a lot  of art now too so i also have books on  art my art  picture books wow and uh and then uh  yeah so there's a lot of different  things i do  besides writing fiction thank goodness  for sd drives and google drive huh  i've just gotta sit on the back burner  that long  okay uh you're always there waiting  calling to me  our next question is has your writing  been affected by your early development  for example school home life and if  that's true which it probably is in what  ways  well uh yes it has been now i grew up my  parents came from spain so we were an  immigrant family  and  they did not they read the newspaper  like cover to cover every every evening  but it was and they stressed education  but we didn't have a lot of books  at the  house um  and in high school by the time i went to  high school i went to a private girls  school and uh  my worst subject in high school was  english i i barely passed it so i did  and i i barely passed two subjects  english and typing and so you know i had  a bad taste in my mouth for that so i  did pursue  writing um  for for a while after that  that being said there were periods  in that i remember like when i was in  grammar school we were asked to write a  prayer  and i wrote a prayer in very quick order  like in 10 minutes and it went into  pride it won a prize  and i did write a short story kind of a  short story in in  in high school  and my mother read it and she was like  you wrote this and she was shocked that  i wrote it so and i always was my  friends always said you write great  letters you know so i was getting i was  getting feedback on odd places  but uh not for fiction and i mean i just  had i i had a thoughts that i just  wasn't a writer i was always much better  in math  so my schooling uh my home life  didn't i mean i wasn't one of those kids  that start reading at three years of age  and start writing their first book at  10. you know a lot of people some i mean  great writers are often like that and  they're obsessed with writing from a  very young age  i started writing  seriously um  after i got out of graduate school i was  40 years old that's when i started to  write the first novel  and that was kind of accidental because  i went to graduate school and i had  young children i was divorced or using  the kids on my own working full time  and i had just finished my master's  program where i did a lot of writing i  didn't do a lot of papers and things  like that so i started like easing into  that whole thing of not being afraid or  not feeling i couldn't do it  in  when i was going to graduate school and  i also bought a computer which made  things so much easier i bought one of  those uh  pow ones which one were those they had  the cow the  uh  i can't remember the name of that  computer it was really expensive but  anyways so i bought a computer with um  with a printer and that's when i started  i had choices i wanted to either go to  graduate school for  my doctorate in social work or go to law  school  or write a novel so i just chose to  write now because i didn't have money or  time to do anything else  wow and that's when i started my  my beginning  uh i saw i started in 1990 in 1996  i joined a writer's group and that  really  solidified my my writing  uh a lot because i was with other  writers and there was a support group  and it was really interesting to be with  other writers  and so having a writing critique like  that in detail was helpful yeah and then  we i started and also i joined a lot of  other small writers groups that were all  working on novels and that was hugely  helpful in my development are you  currently in a writer's group yes i am i  have uh  two people uh come into the house  three people two people yeah there's  three um yeah  yeah there's three of us all together i  draw  yeah you dropped out  i couldn't take the harshness of it  uh here we go um  oh boy if you had enjoyed the freedom to  do so in other words you were not  hampered my words not yours  in other words you you had more free  time by family and the j.o.b  would you have wished to start writing  at a younger age  well that's interesting because  uh no i don't think so because i really  wasn't interested at a younger age and  it is work  i mean it wasn't like a natural  it wasn't natural to me to be a writer  i learned along the way and um  the reason why i'm interested why i was  interested in writing is really it's  about that's why i went into social work  it's about why people do what they do  it's learning it's kind of human nature  that's what draw me to the to writing to  stories about human nature it's not so  much about the act of writing or you  know world building or you know  manipulating characters it's about you  know  looking at someone  uh a character and saying and putting  them in as i said hot water and seeing  what they do  the other thing is it's very interesting  is you do when you write which of course  i never realized any of this it's a lot  about me which i had no idea but when i  look at my stories you know  how the stories are told and what their  challenges are  uh very similar to way you know maybe my  challenges are or  a metaphor for for my own world  so there is that aspect to it too well i  think you answered part two of this or  do you think being hampered as in less  free time has enhanced your writing via  life experience  i think because you had  more time to actually live you got more  right  exactly okay you know i did uh i bought  an electric typewriter before i started  writing before i had married before i  had children i was in my 20s i bought  electric typewriter i thought that would  make things easier because i guess i did  wonder why because people said about my  letter writing was so good so i had i  wrote a paragraph i can't even remember  what it was about i put it in the  typewriter put the typewriter on a desk  in the living room and it sat there for  years the same typewriter  hooked up plugged in with the same piece  of paper wow  i never went beyond that well that  probably needs some dusting  yeah the next quest next question  okay this is the long one and probably  not that good but i found it interesting  for some reason in an essay by george  orwell who we all know wrote animal farm  in 1984 right probably 1984 more than  anything which seems to not go away it's  a story that keeps continuing  as edward snowden and others would point  out to us  he was called his real name was eric  blair i think  wow  but  the little essay that somebody a youtube  sub of mine  mentioned so i went and read it but i  think i read it before it's called why i  write  and he discusses why he became or was a  writer so i have a little link there but  i'll put that in the notes so you can  find if you want to read it so just  a small pdf  so he broke it down as it says here  and i'm saying not the motive behind any  create creative activity matters but  orwell mentions four motives for writing  that he came to after years  and the very first one he says everyone  should admit to is sheer egotism  you're doing it either to become famous  but get recognized because you think  you're clever  or you're just determined or they're  just determined to live their own life  now that one's i'm a little confused by  but what do you think about that as a  motive for writing  i would say that is a very male motive  for writing wow and i would just say i  would argue that's certainly not my  reason uh  for writing if anything i mean it breaks  you know it brings you down i mean you  think you're you're some great writer  you know uh you're special and you read  your stuff and you're being realistic uh  you know it kind of  brings you down a few notches  until you get better at it now clever  fame fortune recognition  uh i think  i can't  for myself that wasn't the reason the  reason was a challenge  to  write something that i felt was good  enough and to put it out there  and whatever happened happened i mean i  would love people to love my work and i  think people do  but  uh if they don't it's okay but i i have  to it's all about  in an egotistic way it's about me  and it's also for me  and um  but it has nothing it's all internal  it's not it's not external it's not fame  it's not  recognition uh i think i am sort of  clever  but i mean i i just think i am clever  now i condensed these down they're a  little bit longer some of them yeah so i  kind of plopped out the things so maybe  i miss a point or two in there well here  egotism i don't think i don't think a  lot of writers would agree with that but  but some would but i i don't agree with  that person okay myself  here's number two of his motives  uh aesthetic enthusiasm  in other words you're just excited about  the beauty of words perception of beauty  in the external world or on the other  hand in words and their right  arrangement i think by writing means  it's pleasing to read  or it grabs you in some way and takes  you away from your you escape a little  bit  and then he went on to say this is the  longest one i got here pleasure in the  impact of one sound on another and the  firm firmness of good pros or the rhythm  of a good story  and a desire to share an experience  which one feels is valuable and ought to  not be to be missed  well i'm not sure about all those points  but aesthetic enthusiasm i think is  definitely because i read a sentence i  can get very excited about a sentence or  a paragraph  um especially when you're working on  something  for a you know i've worked on days on a  paragraph and then i finally get it and  it's like fine you know it's like you  know i want to celebrate  and there is an  uh aestheticness to writing okay and uh  you can definitely be enthusiastic i can  be enthusiastic about that when i read  someone's writing that is just sings  it's it's  you know it's like it's like listening  to a wonderful piece of music or seeing  a beautiful piece of art if i see  writing that it really is beautiful  uh it's it knocks me out now there's uh  just  as one thing that i remember more  recently uh truman capote i never read  his books  i may have read one of his books i'm not  sure but uh i recently in the last five  years read his first short story in the  new yorker it was published when he was  17 or 18 19 years old  and i mean unless my jaw dropped how  someone of that age could write like  that was just  shocking to me and there's a lot of  writers that uh i mean i love writers  for storytelling and then there's other  writers it's just the sheer language is  just breathtaking so  i can understand that part aesthetic  enthusiasm okay  on his motive number three was  uh historical impulse  uh like your own legacy i guess  posterity  the desire to clarify or see maybe  define the truth  you're trying to express  that  impulse in words and stories yeah that's  interesting now  uh  like it will you know books when you  write them uh they will  live they will be around especially now  with you know everything being stored  electronically they could be around for  centuries unless there's a major book  burning or  deleting  yeah yeah  but um  you know stories are interesting i'm not  saying mine are but uh  they are a moment in time especially if  you write a contemporary fiction it can  tell a lot about the times  can also tell you a lot about historical  times if it's historical fiction  so uh writing is important  is an important aspect for this  historical  significance it does have a historical  significance okay  uh  let's go  his fourth one is this is the one he  didn't feel so strong about i believe  was a political purpose you're writing  either to enlighten or expand other  people or you get this strong desire to  fix something and you think your story  1984 is going to fix it before it  happens oops  yes  that could be uh  some writers are definitely in that um  in that position uh  or feel that way about their work now  mine you know i mostly write mysteries  uh i'm writing a few  non-mystery the short stories are more  literary type but that's about the times  um  i try not to have i mean my characters  do have a political lien i'm not  political but they're  uh  i don't tend to write about someone  who's on either any extreme right like i  don't write religious people that are  religious and or some people want them  to be more religious or less religious i  don't write those kind of books you're  not just kind of like trying to i write  about people just trying to get through  their day yeah  you're not out to fix or enlighten  anyone you're not the buddha of writing  okay  okay let's see what what's here  and he did have something i liked in the  little essay where he says good prose is  like a window pane  yeah a lot of ways to look at that froze  and just you know look through and and  see things that's out there beyond  yourself that uh has clarity  and uh it's  you know reading a story is just a  wonderful well it's like  i mean people don't read as much as they  used to but you know you watch a movie  you listen to a radio show i mean that's  what writing is it's just telling it's  telling stories  and and  and it's it's so much a part of human  nature of who we are as humans  that um  it's  it's just a natural  aspect of being human is telling a story  everyone is a storyteller you can think  of your family of origin or my family of  origin and you know at the dinner table  someone tells a story about what  happened at you know work or  on their way home or at school and  people listen you know they listen to  those stories and  sometimes they learn from the stories  and then they tell their own stories  oops  whoops  sorry you went away there for a second i  brought you back  thank you oh wow now you'll be glad to  see that it says end of orwell's motives  so we can go back to normal people  questions  uh if anyone is new to your writing what  would you recommend reading first and  why  well uh  i don't i'd recommend either one of my  mysteries that are novel length  uh if you if someone likes um paloma  yeah paloma is a woman i'll tell you  i'll i'll give you the elevator  thank you paloma is a woman with three  identities  um  someone's after her but she doesn't know  which identity they're after  so she has to revisit her past to draw  the murderer  that's my first novel and uh  it's a great novel and it is it i i'm  using it also stuff word for more of  those novels more of that those  characters haven't quite gotten to that  yet though and then the second one is  another mystery but it's a cozy mystery  not for everybody but it's a little old  lady mystery that has gotten wonderful  reviews  and it's about a woman  uh in her 80s uh who unfortunately finds  it her paper boy dead in her backyard  wow and uh the police say it's the drug  overdose but she knows that  uh jason would never do drugs so she is  going to find out who and why that child  was murdered that's the book murder and  the paccasandra right murder and the  pachy sandra yeah yeah yeah  um  okay so those are two of the ones you  would recommend i might have because i  like short stories i probably would have  thrown in or said  thirst  is that the one oh thirst  they have rented rooms and thirst and  i'll be coming out with another one oh  yeah rented rooms that's right i get  them confused yeah rented rooms is my  first novel my first book that i've ever  published  and you know i opened it up not too long  ago just to see you know  should i um should i unpublish it how  bad is it but it's actually quite good  it's quite good i mean it's it's held up  it's held up quite nicely nice good  are you currently writing  i know yes i am i'm working on  the the second story the second book on  murder in the pachysandra the me it's  called a hattie moon mystery the older  old lady is called hattie moon and i'm  working on her second book which is  howie in love  and that's one of the things i'm working  on right now it's on vela also so  yeah if you read the first book you  could start reading the second book in  bella it's not finished but i'm working  on it  then i'm also working on um i'm working  on a lot of things right now i'm working  on the cure it's an international  thriller  and that's also on vella and it's also  part of the writer's group  and that's something i started in 2005  you know it's it's a lot of fun there's  a lot a lot of interesting characters  you might have to update that one a  little bit given international changes  and interwebs and all that  yeah that's what i have to do  everything's changing okay any thoughts  you want to share since you mentioned  vella and he thought you want to share  about kendall villa there's a wide open  topic  yeah  other than the bonus money  isn't that what it's all about no i  don't think that's what it's supposed to  be all about  but it's nice isn't it  yeah i mean hello you don't even have to  write just slap some words up there 600  of them to be precise  bella you know i keep talking about it  on my youtube channel yeah vela is this  new program with kdp kindle amazon  and what you do is you it's serial so  you write a minimum 600 words whenever  you get to it whenever you want to write  it and you put it up there it can be  it's got to be at least 10  um  10 episodes but it can be a novel length  or  i guess going to you know keep going and  going going  and um  they pay you  to  submit your work not not they don't pay  you for how many reads you get or  anything like that but they're paying  you to write and to submit your writing  and  it's great i mean  it's unheard of  it is on it's unprecedented as well  they call it a bonus though is what  they're calling it a it's called a bonus  because you would get paid  i think somebody estimated and he writes  a lot that he would have gotten each  month maybe maybe maybe five dollars  if he just went by the tokens and the  reads and the likes and all that  when the bonus disappears he'll he said  he'd be crying  because he'd miss out on that money  yeah it's interesting you know  who knows what amazon is doing why  they're doing this or but anyways it's a  windfall for writers  uh if you at all if you write it all  you  slap it up there  just you you it's  it's easy to do it's not hard to do oh  yeah yeah it's a good it's a good deal  it's unheard of it's uh once in a  lifetime maybe  yeah it's a very good deal  so let's let's see what's next is there  anything  else i should say  you would like to say before we end also  note  that i will include links to your stuff  on amazon like your author page and  whatever else you want me to include  that's why i included etc  but is there anything that you would  like to say before we go  well a couple of things actually oh my  goodness uh when do i get to interview  you  to interview someone they have to have  had something  that they've done  other than  have children more  short stories on villa yeah other than  that yeah  so i'm sure maybe someday maybe someday  and you're also well there's a lot of  things you do that is korea are creative  so i mean you could definitely uh be  interviewed for a long time yeah it  might last about five minutes instead of  28 minutes though  we're at 28 minutes right now  yeah  writing uh is something uh you know as i  said earlier is something  you don't need anything you don't need  any special equipment you don't need a  piano your violin you don't need art  materials you know you know how much art  materials can cost once you buy the  canvases or  all you need is a paper and a pencil  and to tell a story and uh  i mean if you're writing fiction or  anything or poetry or  screenplay or anything  so it's something that you can do uh you  don't need to invest a lot just your  time and energy and i would suggest  uh  the thing that made the most difference  for me is certain books made a  difference but  but being in a writer's group is really  uh critical and i say this a lot to a  lot of people and you know you can join  a writer's group in your area or start  one in your local library and that'll  really  you know it's really nice talking with  other writers there's a bunch of online  ones too  yeah but the personal i think when  you're in person it's better in a lot of  ways except for the viruses  well yeah that but that's that's  changing  so hopefully that's changing  but um  when you're a writer you're in your head  a lot  and there's nothing as boring as being  with people  that  that don't write and they don't really  want to hear it you know they don't only  want to hear your stories or what you're  writing or anything like that because  it's like telling about a movie you know  you go to a dinner party and someone  tells you about a movie talks about them  you know you want to see the movie you  want to be there you don't want to have  something to tell you yeah  that's true so  so with writers uh everyone it's not  just a story but it's the the writing  it's where they're getting their ideas  from it's also honing the skill  so it is really nice to be in a small  group  of writers and uh and and actually i  don't care where you live they're out  there those writers they just are  hidden or you know they're not  very social because they're writers  they're kind of quiet and keeping to  themselves i guess that would lead me to  a bonus question  which is  what if you  have absolutely zero desire to publish  your stuff anywhere you almost like  you're just writing in a journal for  yourself the stories are for you they're  not for anybody else does that  still count as a writer an author oh  that counts as a writer and an author  for sure yeah i mean there are writers  that uh  that that's what they did i mean they  wrote books but then a lot of them you  know they just quieted down and  wrote their memoirs or something  privately and  yeah that counts as a writer now would  they want to come out and talk about it  i don't know maybe they would  memoirs are very popular people do work  on memoirs and that's that's being a  writer and everyone's got a great story  to tell if if not many many stories to  tell about their lives  there was this uh this thing they do in  europe and it's it's a great  idea and it could be done here where  people meet i don't know if they meet  they meet at um  coffee houses coffee  cafes you know  and uh they're encouraged to sit  sit next to someone and and and talk to  them about their life you know exchange  life stories  and uh that's a great idea because it is  all about story and as i said earlier  stories are  just part of being human and so  that you get in touch with that kind of  thing through writing  okay or it can be an oral it can be a  storytelling an oral tradition as well  obviously with fairy tales and all that  sort of thing  well  for my part here i'll say thank you for  letting me interview you  you're welcome and i'll say thank you to  this overpriced slightly hard to learn  how to use  ecamm  that if you can afford it my gosh get it  if you want to put something on  [Music]  if it took you two minutes to do it's  done in two minutes this took us  32 minutes as soon as i hit that button  over there which we're going to wait on  but as soon as i do it's there  you could go watch it you don't wait for  anything to happen it's done wow it's  amazing but it's way overpriced way  way overpriced  so let me get rid of these notes here  and let your  it is four hundred dollars per  year  a year per year  wow  wow that prices a lot of people out of  the market i think it does and only on  apple and only on an imac  oh wow and yeah wow  i was right that's a little that's a  little steep for a lot of people that is  that's  yeah but they're all over it  i'll just use my phone and go on youtube  that's what you do  so we're going to hang here for a little  bit and i can't guarantee what happens  but i'm going to do this ahead of time  or so if there's something you want to  say  go ahead and say it like peace or  whatever no yeah thanks for the  interview it was fun thank you and i'll  say peace and then we're gonna hang  because there's no telling when this  ends that's its little flaw so far  so i'm gonna let go and babble babble so  i'll get cut off at some
</raw_transcript_text>
""",
        }
    ],

    model="llama3-70b-8192",
    # model="gemma-7b-it", # cls: lame, it only does summaries

    #
    # Optional parameters
    #

    # Controls randomness: lowering results in less random completions.
    # As the temperature approaches zero, the model will become deterministic
    # and repetitive.
    temperature=0,

    # The maximum number of tokens to generate. Requests can use up to
    # 2048 tokens shared between prompt and completion.
    max_tokens=8192,

    # Controls diversity via nucleus sampling: 0.5 means half of all
    # likelihood-weighted options are considered.
    top_p=1,

    # A stop sequence is a predefined or user-specified text string that
    # signals an AI to stop generating content, ensuring its responses
    # remain focused and concise. Examples include punctuation marks and
    # markers like "[end]".
    stop=None,

    # If set, partial message deltas will be sent.
    stream=True,
)

# Print the incremental deltas returned by the LLM.
for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
