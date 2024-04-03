"""
FreeGenius AI Plugin - conselling

add contexts for conselling

"""

"""
# Information

>>> What are popular approaches of counselling?

There are several popular approaches to counseling that are commonly used by therapists and counselors. Here are some of the most well-known approaches:

1. Cognitive Behavioral Therapy (CBT): CBT is a goal-oriented approach that focuses on identifying and changing negative thought patterns and behaviors. It helps individuals develop healthier coping strategies and improve their overall well-being.

2. Psychodynamic Therapy: This approach explores how past experiences and unconscious thoughts and feelings influence current behaviors and relationships. It aims to bring awareness to unresolved conflicts and promote emotional healing.

3. Humanistic Therapy: Humanistic therapy emphasizes personal growth, self-awareness, and self-acceptance. It focuses on the present moment and encourages individuals to take responsibility for their actions and make positive changes.

4. Solution-Focused Brief Therapy (SFBT): SFBT is a short-term, goal-oriented approach that focuses on finding solutions rather than dwelling on problems. It helps individuals identify their strengths and develop practical strategies to achieve their desired outcomes.

5. Family Systems Therapy: This approach considers the family as a whole and examines how individual members' behavior and interactions affect the entire system. It seeks to improve communication, promote understanding, and resolve conflicts within the family unit.

6. Gestalt Therapy: Gestalt therapy emphasizes self-awareness and personal responsibility. It encourages individuals to focus on the present moment, develop a deeper understanding of themselves, and integrate different aspects of their personality.

7. Existential Therapy: Existential therapy explores the meaning and purpose of life and helps individuals confront existential concerns such as loneliness, mortality, and freedom. It encourages individuals to take responsibility for their choices and create a meaningful existence.

8. Mindfulness-Based Therapy: This approach incorporates mindfulness practices, such as meditation and breathing exercises, to help individuals become more present and aware of their thoughts and emotions. It can be effective in managing stress, anxiety, and depression.

9. Narrative Therapy: Narrative therapy focuses on the stories we tell ourselves about our lives and experiences. It helps individuals reframe negative narratives and create new, empowering narratives that promote growth and change.

10. Adlerian Therapy: Adlerian therapy is based on the principles of Alfred Adler and focuses on exploring an individual's unique lifestyle and social context. It emphasizes the importance of social connections, personal responsibility, and goal setting.

11. Emotion-Focused Therapy (EFT): EFT focuses on the emotions underlying a person's thoughts and behaviors. It helps individuals understand and regulate their emotions, improve their relationships, and create a more fulfilling life.

12. Rational Emotive Behavior Therapy (REBT): REBT is a cognitive-behavioral approach that focuses on identifying and challenging irrational beliefs and replacing them with healthier, more rational thoughts. It aims to help individuals develop resilience and cope with life's challenges.

13. Motivational Interviewing: Motivational interviewing is a collaborative approach that helps individuals explore and resolve ambivalence towards change. It is often used to address issues such as addiction, weight management, and behavior change.

14. Trauma-Informed Therapy: Trauma-informed therapy recognizes the impact of past trauma on an individual's mental health and well-being. It focuses on creating a safe and supportive environment and employs strategies to help individuals process and heal from trauma.

15. Person-Centered Therapy: Person-centered therapy, also known as client-centered therapy, emphasizes the importance of the therapeutic relationship and unconditional positive regard. It focuses on providing a safe and non-judgmental space for individuals to explore their thoughts, feelings, and experiences.

16. Dialectical Behavior Therapy (DBT): DBT was originally developed to treat individuals with borderline personality disorder, but it has since been adapted for other conditions as well. It combines elements of cognitive-behavioral therapy with mindfulness practices to help individuals regulate emotions, improve interpersonal relationships, and develop coping skills.

17. Reality Therapy: Reality therapy focuses on addressing the present needs and choices of individuals, emphasizing personal responsibility and accountability. It helps individuals identify and make more effective choices to meet their needs and achieve their goals.

18. Cognitive Analytic Therapy (CAT): CAT combines elements of cognitive therapy and psychoanalytic therapy. It aims to understand how past experiences and patterns of thinking influence current difficulties and helps individuals develop new ways of thinking and behaving.

19. Integrative Therapy: Integrative therapy combines elements from different therapeutic approaches to create a tailored and flexible treatment plan. It recognizes that individuals are unique and may benefit from incorporating a variety of techniques and strategies to address their specific needs.

20. Narrative Exposure Therapy (NET): NET is a trauma-focused therapy that aims to help individuals process and integrate traumatic memories. It involves recounting and reorganizing traumatic experiences within a coherent narrative, promoting healing and resilience.

21. Acceptance and Commitment Therapy (ACT): ACT focuses on developing psychological flexibility by accepting difficult thoughts and emotions while committing to taking action aligned with personal values. It aims to help individuals live a meaningful and valued life, even in the presence of challenging experiences.

22. Transpersonal Therapy: Transpersonal therapy explores beyond the individual's personal identity and focuses on spiritual and transcendent aspects of human experience. It may involve practices such as meditation, visualization, and exploring existential questions.
"""

from freegenius import config

approaches = (
    "Cognitive Behavioral Therapy (CBT)",
    "Psychodynamic Therapy",
    "Humanistic Therapy",
    "Solution-Focused Brief Therapy (SFBT)",
    "Family Systems Therapy",
    "Gestalt Therapy",
    "Existential Therapy",
    "Mindfulness-Based Therapy",
    "Narrative Therapy",
    "Adlerian Therapy",
    "Emotion-Focused Therapy (EFT)",
    "Rational Emotive Behavior Therapy (REBT)",
    "Motivational Interviewing",
    "Trauma-Informed Therapy",
    "Person-Centered Therapy",
    "Dialectical Behavior Therapy (DBT)",
    "Reality Therapy",
    "Cognitive Analytic Therapy (CAT)",
    "Integrative Therapy",
    "Narrative Exposure Therapy (NET)",
    "Acceptance and Commitment Therapy (ACT)",
    "Transpersonal Therapy",
)

for approach in approaches:
    config.predefinedContexts[f"Counselling - {approach}"] = f"""I want you to act as a counsellor using {approach}.
[CHAT]"""